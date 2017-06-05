
import pika
import logging
from time import sleep
from random import randint

logging.basicConfig(filename='example.log',level=logging.INFO)

logger = logging.getLogger(__name__)

class BasicConsumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, conn_para, exchange=None, exchange_type=None,
                 queue=None, routing_key=None):
        """Create a new instance of the consumer class, passing in the 
        connection parameters used to connect to RabbitMQ.

        :param dict conn_para: The parameters for connection, include username,
        password, host, port, virtual_host, heartbeat_interval, and so on.

        """
        self.credentials = pika.PlainCredentials(conn_para.pop('username'),
                                                 conn_para.pop('password'))
        self.conn_para = pika.ConnectionParameters(
                                        credentials = self.credentials,
                                        **conn_para)
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key
        
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

    def connect_and_start(self):
        """Connects to RabbitMQ. When ioloop start and connections established, 
        the event will trigger pika to call the method on_connection_open. When
        RabbitMQ closes the connection unexpectedly, pika call the mehtod
        on_connection_closed

        """
        logger.info('Connecting to %s', self.conn_para)
        self._connection =  pika.SelectConnection(self.conn_para,
                                                  stop_ioloop_on_close=False)
        
        self._connection.add_on_open_callback(self.on_connection_open)
        self._connection.add_on_close_callback(self.on_connection_closed)
        
        self._connection.ioloop.start()
        

    def on_connection_open(self, connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established.

        :type connection: pika.SelectConnection

        """
        logger.info('Connection opened, create a new channel...')
        # Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        # command. When RabbitMQ responds that the channel is open, the
        # on_channel_open callback will be invoked by pika.
        connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        if self._closing:
            self._channel = None
            self._connection.ioloop.stop()
            logger.info('close connection normally.')
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            def reconnect():
                self._connection.ioloop.stop()
                self.connect_and_start()
            
            self._connection.add_timeout(5, reconnect)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        :param pika.channel.Channel channel: The channel object

        """
        logger.info('Channel opened, add channel close callback...')
        channel.add_on_close_callback(self.on_channel_closed)
        self._channel = channel
        
        if not self.exchange:
            logger.info('declare queue connect to the default exchange...')
            self._channel.queue_declare(self.on_queue_declareok, self.queue)
        else:
            logger.info('Declaring exchange %s...', self.exchange)
            # Setup the exchange on RabbitMQ by invoking the Exchange.Declare 
            # RPC command.
            self._channel.exchange_declare(self.on_exchange_declareok,
                                           self.exchange,
                                           self.exchange_type)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_exchange_declareok(self, frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method frame: Exchange.DeclareOk response frame

        """
        logger.info('Exchange declared, Declaring queue %s...', self.queue)
        # Setup the queue on RabbitMQ by invoking the Queue.Declare RPC command.
        self._channel.queue_declare(self.on_queue_declareok, self.queue)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        if not self.exchange:
            self.start_consuming()
        else:
            logger.info('Binding %s to %s with %s',
                        self.exchange, self.queue, self.routing_key)
            self._channel.queue_bind(self.on_bindok, self.queue,
                                     self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        logger.info('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        logger.info('Issuing consumer related RPC commands')
        # If RabbitMQ cancel the consumer, on_consumer_cancelled will be invoked
        # by pika.
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.queue)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        print body
        sleep(randint(1,3))
        
        logger.info('Acknowledging message %s', basic_deliver.delivery_tag)
        self._channel.basic_ack(basic_deliver.delivery_tag)
    
    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        logger.info('RabbitMQ acknowledged the cancellation of the consumer,'
                    'close the channel')
        self._channel.close()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        logger.info('Stopping')
        self._closing = True
        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)
        self._connection.ioloop.start()
        logger.info('Stopped')


class RoundRobinConsumer(BasicConsumer):
    def on_channel_open(self, channel):
        logger.info('Channel opened, set prefetch_count=1')
        channel.basic_qos(prefetch_count=1)
        BasicConsumer.on_channel_open(self, channel)
        

class FanoutConsumer(BasicConsumer):
    def __init__(self, conn_para, exchange):
        BasicConsumer.__init__(self, conn_para, exchange=exchange, 
                               exchange_type='fanout')

    def on_exchange_declareok(self, frame):
        #override
        logger.info('Exchange declared, Declaring queue %s...', self.queue)
        
        self._channel.queue_declare(self.on_queue_declareok,
                                    exclusive=True)
        
    def on_queue_declareok(self, method_frame):
        self.queue = method_frame.method.queue
        logger.info('Binding %s to %s with %s',
                    self.exchange, self.queue, self.routing_key)
        self._channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange)


class DirectConsumer(BasicConsumer):
    def __init__(self, conn_para, exchange, routing_keys):
        BasicConsumer.__init__(self, conn_para, exchange=exchange, 
                               exchange_type='direct', routing_key=routing_keys)
    
    
    def on_exchange_declareok(self, frame):
        logger.info('Exchange declared, Declaring queue %s...', self.queue)
        self._channel.queue_declare(self.on_queue_declareok,
                                    exclusive=True)
        
    def on_queue_declareok(self, method_frame):
        self.queue = method_frame.method.queue
        logger.info('Binding %s to %s with %s',
                    self.exchange, self.queue, self.routing_key)
        for key in self.routing_key:
            self._channel.queue_bind(self.on_bindok, self.queue,
                                     self.exchange, key)



    

        
        
        