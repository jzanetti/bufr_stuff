#!/usr/bin/env python

""" Setup for bufr stuff """

from glob import glob
from setuptools import find_packages, setup
from os.path import basename, dirname, realpath

def main():
    return setup(
        author='Sijin Zhang',
        author_email='Sijin.Zhang@metservice.com',
        data_files=[('bufr_stuff/etc', glob('etc/*')), ('bufr_stuff/script', glob('script/*'))],
        description='Script for running bufr',
        maintainer='Sijin Zhang',
        maintainer_email='Sijin.Zhang@metservice.com',
        # Use name of the directory as name
        name=basename(dirname(realpath(__file__))),
        packages=find_packages(),
        zip_safe=False
    )

if __name__ == '__main__':
    main()
