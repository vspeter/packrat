#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import packrat

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = packrat.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='packrat',
    version=version,
    description="""A Single interface for managing aptand yum repos""",
    long_description=readme + '\n\n' + history,
    author='EMC Case Team',
    author_email='autobots@emc.com',
    url='https://github.emcrubicon.com/pantry-dev/packrat',
    packages=[
        'packrat',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='packrat',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)