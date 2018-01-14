#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='SauceNAO',
      version='0.0.1',
      description='Small module to work with SauceNAO locally',
      url='https://github.com/DaRealFreak/saucenao',
      author='DaRealFreak',
      author_email='steffen.keuper@web.de',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'bs4',
          'requests'
      ],
      extras_require={
          'unittests': [
              'python-dotenv',
              'Pillow'
          ]
      },
      zip_safe=True)
