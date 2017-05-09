
from distutils.core import setup, Extension

module1 = Extension('basic_func',
                    sources = ['basic_func.c'])

module2 = Extension("simple_obj", ["simple_obj.c"])

module3 = Extension("sort_example", ["sort_example.c"])

setup (name = 'basic',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1, module2, module3])
