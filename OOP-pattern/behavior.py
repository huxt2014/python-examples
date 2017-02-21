

###############################################################################
#                        replace observer with signal/event
###############################################################################

import blinker


class Supervisor(object):
        
    sig_alarm = blinker.signal('alarm')
    
    def __init__(self, id):
        self.id = id
    
    def alarm(self):
        print '%s-th supervisor alarm.' % self.id
        self.sig_alarm.send(self)


class Worker(object):
    
    def __init__(self, id):
        self.id = id
        Supervisor.sig_alarm.connect(self.on_alarm)
        
    def on_alarm(self, sup):
        print '%s-th worker get alarm from %s-th supervisor' % (self.id, sup.id)


s = Supervisor(1)
workers = [Worker(i) for i in range(1, 5)]
s.alarm()
