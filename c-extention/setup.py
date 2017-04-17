
from distutils.core import setup, Extension

module1 = Extension('basic_func',
                    sources = ['basic_func.c'])

setup (name = 'basic_func',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
