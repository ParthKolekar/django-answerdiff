#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import answerdiff

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = answerdiff.__version__

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-answerdiff',
    version=version,
    description="""Checking Submissions the Boss Way using Celery and DRF""",
    long_description=readme + '\n\n' + history,
    author='Parth Kolekar',
    author_email='parth.kolekar@students.iiit.ac.in',
    url='https://github.com/ParthKolekar/django-answerdiff',
    packages=[
        'answerdiff',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-answerdiff',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
