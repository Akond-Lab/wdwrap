# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='wdwrap',
    version='0.1.0',
    description='Sample package description',
    long_description=readme,
    author='Mikolaj Kaluszynski',
    author_email='mkalusz@camk.edu.pl',
    url='',
    license=license,
    packages=find_packages(exclude=('tests'))
)
