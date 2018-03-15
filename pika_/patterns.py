"""
    Three keys of AMQP 0-9-1 is sender routing key, receiver routing key and
exchange type.
    A DIRECT exchange delivers messages to each queue whose routing key exactly
matches the sender routing key. A FANOUT exchange routes messages to all of the
queues that are bound to it and the routing key is ignored. A TOPIC exchange
delivers messages to each queue whose routing key looks like the sender routing
key.
    RabbitMQ has a default exchange, which is a direct exchange. Every queue
that is created is automatically bound to it with a routing key which is the
same as the queue name.
"""

import pika
import time

###############################################################################
#                                simple
###############################################################################

# sender ###################################################
connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

# Use default exchange. Routing_key are the same with queue
# name, so exchange will send the message to the target queue
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()


# receiver #################################################
connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# declare again, to ensure the queue exists.
channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)   # send ack automatically

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()


###############################################################################
#                             work queue
#     Use default exchange, whose type is direct exchange. All workers share
# one queue. Sender routing key is the same as queue name. Bind is automatically
# performed with a routing key that is the same as the queue name.
###############################################################################

# sender ###################################################

# make the queue not deleted when sender or receiver exit.
channel.queue_declare(queue='task_queue', durable=True)

message = "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode=2,  # make message persistent
                      ))
print(" [x] Sent %r" % message)
connection.close()

# receiver #################################################

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

# tell RabbitMQ not to give more than one message to a worker
# at a time
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()

###############################################################################
#                               broadcast
#     Use fanout exchange. Each worker has its own queue. Sender routing_key is
# empty. Receiver routing_key is None.
###############################################################################

# sender ###################################################

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

message = "info: Hello World!"
channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(" [x] Sent %r" % message)
connection.close()

# receiver #################################################

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

# queue will be deleted when this receiver exit, and
# let RabbitMQ name this queue.
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs',
                   queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

###############################################################################
#                         publisher and subscriber
#     Use direct exchange, whose routing algorithm is sender routing_key exactly
# matches receiver routing_key and broadcast on routing_key. Each worker has its
# own queue. Sender routing_key is message_type. Receiver routing_key is
# message_type.
###############################################################################

# sender ###################################################
channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

severity = 'info'  # or warn, error
message = 'Hello World!'
channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)
print(" [x] Sent %r:%r" % (severity, message))
connection.close()


# receiver #################################################

channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

# can bind several times and receive not only one kind of message
severities = ["error", "warn"]
for severity in severities:
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

###############################################################################
#                             topic subscriber
#     Use topic exchange, whose routing algorithm is sender routing_key looks
# like receiver routing_key and broadcast on routing_key. Each worker has its
# own queue. Sender routing_key is topic. Receiver routing_key is topic.
###############################################################################

