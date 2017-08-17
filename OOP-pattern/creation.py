"""
    Sometimes creational patterns overlap. There are cases when either prototype
or abstract factory would be appropriate. At other times they complement each
other: abstract factory might store a set of prototypes from which to clone and
return product objects (GoF, p126). Abstract factory, builder, and prototype can
use singleton in their implementations. (GoF, p81, 134). Abstract factory
classes are often implemented with factory methods, but they can be implemented
using prototype (creation through delegation). (GoF, p95)
    Often, designs start out using Factory Method (less complicated, more
customizable, subclasses proliferate) and evolve toward abstract factory,
prototype, or builder (more flexible, more complex) as the designer discovers
where more flexibility is needed.

    Some pattern aren't really needed for Python at all. This is because the
original design patterns were primarily created for the C++ language and needed
to work around some of that language's limitations. Python doesn't have those
limitations.
"""

import copy
import functools


###############################################################################
#                              Factory Pattern
###############################################################################
class FactoryMeta(type):
    """
    Class that use this meta act as factory class.
    """
    def __call__(cls, *args, **kwargs):
        
        cls_str = 'some class'
        instance = type.__call__(FactoryMeta.cls_map.get(cls_str, cls),
                                 *args, **kwargs)
        return instance
    
    cls_map = {'list': list,
               'tuple': tuple}
    

class FactoryClass(object):
    """
    Using __new__ to intercept instance creation.
    """
    
    def __new__(cls, *args, **kwargs):
        concrete_cls = list
        return concrete_cls(*args, **kwargs)


def get_instance(class_str, *args, **kwargs):
    """
    Factory function
    """
    return globals()[class_str](*args, **kwargs)


###############################################################################
#                          Abstract Factory Pattern
#     The Abstract Factory Pattern is designed for situations where we want to
# create complex objects that are composed of other objects and where the
# composed objects are all of one particular "family".
###############################################################################

class AbsFactory():
    
    @classmethod
    def make_instance(cls):
        c3 = cls.C3()
        c3.add_c1(cls.C1())
        c3.add_c2(cls.C2())
        
        return c3
    
    class C1:
        def __init__(self):
            pass
    
    class C2:
        def __init__(self):
            pass
    
    class C3:
        
        def __init__(self):
            pass
        
        def add_c1(self, cpu):
            pass
        
        def add_c2(self, disk):
            pass


###############################################################################
#                               Builder Pattern
#     Unlike the abstract factory pattern and the factory method pattern whose
# intention is to enable polymorphism, the intention of the builder pattern is
# to find a solution to the complicated construction: the increase of object
# constructor parameter combination leads to an exponential list of
# constructors.
#     Instead of using numerous constructors, the builder pattern uses another
# object, a builder, that receives each initialization parameter step by step
# and then returns the resulting constructed object at once.
###############################################################################

class Director:

    def __init__(self, builder):
        self.builder = builder

    def construct(self, **kwargs):
        # do complicated initialization. Builder do the job, and the director
        # control how the job is done.
        self.builder.step1()
        if kwargs['par1']:
            self.builder.step2()
        if kwargs['par2']:
            self.builder.step3()
        self.builder.step4()
        return self.builder.result()


###############################################################################
#                            Lazy initialization
#     Delaying the creation of an object, the calculation of a value, or some
# other expensive process until the first time it is needed.
###############################################################################

class lazy_property(object):
    """
    Use descriptor.
    """
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __get__(self, instance, owner):
        """
        :param instance: the instance through which the attribute was accessed.
        Or None if the attribute is accessed through the owner class directly.
        :param owner: the class to which the descriptor instance is attached.
        """
        # call the method
        result = self.function(instance)
        # replace the attribute
        instance.__dict__[self.function.__name__] = result
        return result


class Lazy:

    _value1 = None

    def __init__(self, base_value):
        self.base_value = base_value

    @property
    def value1(self):
        if not self._value1:
            # expensive process
            self._value1 = self.base_value
        return self._value1

    @lazy_property
    def value2(self):
        return self.base_value


###############################################################################
#                              Singleton Pattern
#     Ensure a class has only one instance, and provide a global point of access
# to it.
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


class singleton_c:
    """
    Implement the singleton pattern using class
    """

    def __init__(self, inner_cls):
        self.inner_cls = inner_cls
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.inner_cls(*args, **kwargs)
        return self.instance


###############################################################################
#                             Prototype Pattern
#     Create the objects from prototypical instance, usually through clone. It
# is often used when the cost of initialization is expensive.
###############################################################################
class Prototype(object):

    value = 'default'

    def clone(self, **kwargs):
        obj = copy.deepcopy(self)
        obj.__dict__.update(**kwargs)
        return obj
