from setuptools import setup, find_packages
import codecs
import os
import ibclient

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = """
IBClient
===============

"""

setup(
    name='IBClient',
    version=ibclient.__version__,
    description='A Python based IB TWS client interface',
    long_description = long_desc,
    author='Jin Xu',
    author_email='jin_xu1@qq.com',
    license='BSD',
    keywords='IB TWS interface',
    classifiers=['Development Status :: 1 - Alpha',
    'Programming Language :: Python :: 2.7',
    'License :: OSI Approved :: BSD License'],
    packages=['ibclient'],
)