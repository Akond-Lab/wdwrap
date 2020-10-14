# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from wdwrap.version import __version__

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='wdwrap',
    version=__version__,
    description='WD code wrapper',
    long_description=readme,
    author='Mikolaj Kaluszynski (AkondLab, CAMK)',
    author_email='mkalusz@camk.edu.pl',
    url='',
    license=license,
    packages=find_packages(exclude=('tests'))
)
