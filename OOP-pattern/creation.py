'''
    Some pattern aren't really needed for Python at all. This is because the
original design patterns were p6rimarily created for the C++ language and needed
to work around some of that language's limitations. Python doesn't have those
limitations.
'''

###############################################################################
#                              Factory Pattern
###############################################################################       
            
class FactoryMeta(type):
    """
    Implement factory pattern using metaclass.
    """
    def __call__(cls, *args, **kwargs):
        
        cls_str = 'some class'
        instance = type.__call__(FactoryMeta.cls_map.get(cls_str, cls),
                                 *args, **kwargs)
        return instance
    
    cls_map = {'list': list,
               'tuple': tuple}


###############################################################################
#                          Abstract Factory Pattern
#    The Abstract Factory Pattern is designed for situations where we want to
#create complex objects that are composed of other objects and where the
#composed objects are all of one particular "family".
###############################################################################

class DellFactory():
    
    @classmethod
    def make_computer(cls):
        computer = cls.Computer()
        computer.add_cpu(cls.Cpu())
        computer.add_disk(cls.Disk())
        
        return computer
    
    class Cpu():
        def __init__(self):
            self.content = 'AMD cpu'
    
    class Disk():
        def __init__(self):
            self.content = 'SATA disk'
    
    class Computer():
        
        def __init__(self):
            self.content = 'Dell computer'
        
        def add_cpu(self, cpu):
            self.cpu = cpu
        
        def add_disk(self, disk):
            self.disk = disk

        def show(self):
            print '%s has %s and %s' % (
                    self.content, self.cpu.content, self.disk.content)
    
    
class AppleFactory():
    
    @classmethod
    def make_computer(cls):
        computer = cls.Computer()
        computer.add_cpu(cls.Cpu())
        computer.add_disk(cls.Disk())
        
        return computer

    class Cpu():
        def __init__(self):
            self.content = 'Intel cpu'
    
    class Disk():
        def __init__(self):
            self.content = 'SSD disk'

    
    class Computer():
        
        def __init__(self):
            self.content = 'Apple computer'
        
        def add_cpu(self, cpu):
            self.cpu = cpu
        
        def add_disk(self, disk):
            self.disk = disk

        def show(self):
            print '%s has %s and %s' % (
                    self.content, self.cpu.content, self.disk.content)


        
###############################################################################
#                              Singleton Pattern
############################################################################### 
      
def singleton(cls):
    """
    Implement the singleton pattern using function and closure.
    """

    def inner_func(*args, **kwargs):
        if inner_func.instance is None:
            inner_func.instance = cls(*args, **kwargs)
        return inner_func.instance
        
    inner_func.instance = None
    return inner_func
    
class SingletonMeta(type):
    """
    Implement the singleton pattern using metaclass.
    """
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = type.__call__(cls, *args, **kwargs)
        return cls.instance
    


