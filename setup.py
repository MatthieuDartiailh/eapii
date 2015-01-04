#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
try:
    import sys
    reload(sys).setdefaultencoding("UTF-8")
except:
    pass


try:
    from setuptools import setup, find_packages
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)


import codecs


def read(filename):
    return codecs.open(filename, encoding='utf-8').read()


long_description = '\n\n'.join([read('README.rst'),
                                read('AUTHORS'),
                                read('CHANGES')])

__doc__ = long_description

setup(name='eapii',
      description='Easy Python instrument interfacing',
      version='0.1.0dev',
      long_description=long_description,
      author='Matthieu Dartiailh',
      author_email='m.dartiailh@gmail.com',
      url='https://github.com/MatthieuDartiailh/pyvisa',
      requires=['future', 'pint'],
      install_requires=['future', 'pint'],
      keywords='instrument interfacing measurement',
      license='Modified BSD',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          ],
      packages=find_packages(),
      platforms="Linux, Windows, Mac",
      use_2to3=False,
      zip_safe=False)
