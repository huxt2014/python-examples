

##############################################################################
#                          customize class creation
#     By default, after class statement is executed, Python call the type object
# to create the class object, like this: type(cls_name, supers, attr_dict). The
# type object in turn invoke __call__ method, in which, function __new__ and
# __init__ is invoked.
#     If __metaclass__ of class is set, for example, as Meta, then, after class
# statement is executed, Python call Meta() to create the class object instead
# of type().
#     Metaclass can be defined by inheriting type object and override __call__,
#  __new__ and __init__. It can also be any callable object that return a class
# object when called.

# WARNING: if type.__call__ is called explicitly and the first argument is
# passed a class object that __metaclass__is specified, but not a metaclass,
# then __call__ will invoke the cls.__init__ and return an instance of the
# class, but not a class object.
##############################################################################


class Meta(type):

    def __call__(cls, cls_name, supers, attr_dict):
        """
        This method will never be triggered implicitly by calling Meta, but
        can only be triggered implicitly by calling subclass of Meta or
        instance of Meta.

        :param cls: any metaclass, Meta by default
        :param cls_name: name of the class that to be generated
        :param supers: super classes that listed in class statement
        :param attr_dict: attributes that are defined in class statement
        :return: a class object
        """

        return type.__call__(cls, cls_name, supers, attr_dict)

    def __new__(mcs, cls_name, supers, attr_dict):
        """

        :param mcs: metaclass that passed to type
        :return: a class object that not initialized yet
        """
        print('here is __new__')
        return type.__new__(mcs, cls_name, supers, attr_dict)

    def __init__(cls, cls_name, supers, attr_dict):
        """

        :param cls: the class object that to be initialized
        """
        print('here is __init__')
        type.__init__(cls, cls_name, supers, attr_dict)


##############################################################################
#                          inheritance algorithm
##############################################################################
"""
1. Look up an attribute name explicitly from an instance I:
    a. Search the __dict__ of all classes on the __mro__ found at I's __class__
    b. If a data descriptor was found in step a, call it and exit
    c. Else, return a value in the __dict__ of the instance I
    d. Else, call a nondata descriptor or return a value found in step a

2. Look up an attribute name explicitly from a class C:
    a. Search the __dict__ of all metaclasses on the __mro__ found at C's
       __class__
    b. If a data descriptor was found in step a, call it and exit
    c. Else, call a descriptor or return a value in the __dict__ of a class on
       C's own __mro__
    d. Else, call a nondata descriptor or return a value found in step a

3. Look up an attribute name implicitly(built-in operations) from an instance
   or class, just step 1-a and 2-a.

4. On top of all this, method __getattr__ may be run if defined when an
   attribute is not found, and method __getattribute__ may be run for every
   attribute fetch,
"""

##############################################################################
#                       intercept instance creation
# using __new__
#     When a class, for example, Foo is called. Foo.__new__ is called first, and
# then Foo.__init__ is called, and then a instance of Foo got. We can override
# __new__ to intercept the instance creation.
#     If __new__ return an instance of cls, then __init__ will be invoked. If
# __new__ does not return an instance of cls, then __init__ will not be invoked.
#     only for new style class.
#
# using __call__
#     In fact, if Foo is specified a metaclass Meta, and Meta.__call__ exists,
# then Meta.__call__ is invoked before Foo.__new__.

##############################################################################


class Foo(object):

    def __new__(cls, *args, **kwargs):
        """
        This is a static method. Its first argument is the class of which an
        instance is requested. The remaining arguments are all passed to
        __init__.

        :return: any object
        """
        pass

    def __init__(self,  *args, **kwargs):
        pass


##############################################################################
#                            inspect
##############################################################################

class Test:
    pass

# get class name
print(Test.__name__)


##############################################################################
#                            dynamic operation
##############################################################################

import importlib
import imp

# import module
os = importlib.import_module('os')              # import os
path = importlib.import_module('.path', 'os')   # import os.path
