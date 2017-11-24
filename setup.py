#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = open('requirements.txt').readlines()

setup(
    name='comicd',
    version='0.0.1',
    author='fancxxy',
    author_email='fancxxy@gmail.com',
    url='https://github.com/fancxxy/comicd',
    description='comic download tool',
    license='MIT',
    classifiers=[],
    packages=find_packages(exclude=('tests',)),
    install_requires=requirements
)
