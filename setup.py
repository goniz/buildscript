__author__ = 'gz'

from distutils.core import setup

setup(
    name='build-system',
    version='0.1.0',
    author='gz',
    author_email='goni1993@gmail.com',
    packages=['build_system'],
    scripts=['bin/build.py'],
    url='https://github.com/goniz/buildscript',
    description='python-based build system',
    requires=['termcolor']
)
