
import sys
from distutils.core import setup, Extension

m_ipstore_2_3 = Extension("ip_store", ["ip_store.c"])
m_func_example_2_3 = Extension('basic_func',
                               sources=['basic_func.c'])

m_obj_example_2 = Extension("simple_obj", ["simple_obj.c"])

m_sort_3 = Extension("sort_example", ["sort_example.c"])
m_tree_3 = Extension("tree", ["tree.c"])


m_list = [m_func_example_2_3, m_ipstore_2_3]
if sys.version_info[0] == 3:
    m_list.extend([m_sort_3, m_tree_3])
else:
    m_list.extend([m_obj_example_2])

setup (name='basic',
       version='1.0',
       description='This is a demo package',
       ext_modules=m_list)
