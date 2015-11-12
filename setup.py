# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='chrony',
    version='0.1.0',
    author='Guillaume Thomas',
    author_email='guillaume.thomas@optimdata.eu',
    license='LICENSE',
    description='Timeseries analysis tools with specific focus on timespans. Built on top of pandas.',
    url='https://github.com/optimdata/chrony',
    include_package_data=True,
    packages=find_packages(),
)
