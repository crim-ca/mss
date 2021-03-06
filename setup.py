#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setuptools configuration script.
"""

from mss.__meta__ import __version__, __author__, __contact__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    README = readme_file.read()
    DESC = README.split('\n')[0]

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read().replace('.. :changelog:', '')

REQUIREMENTS = ['VestaRestPackage==1.9.3']

setup(
    # -- Meta information --------------------------------------------------
    name='mss',
    version=__version__,
    description=DESC,
    long_description=README + '\n\n' + HISTORY,
    author=__author__,
    author_email=__contact__,
    url='http://www.crim.ca',
    license="copyright CRIM 2015",
    platforms=['linux-x86_64'],
    keywords='CANARIE, Swift, OpenStack, File Hosting, Multimedia, Services',
    classifiers=[
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    # -- Package structure -------------------------------------------------
    packages=['mss'],

    install_requires=REQUIREMENTS,
    zip_safe=False,

    exclude_package_data={'mss': ['.hg', '.hglf']},

    package_data={
        'mss': ['static/*', 'templates/service/*']
        }
    )
