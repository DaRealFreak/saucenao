#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='SauceNAO',
      version='0.0.1',
      description='Small module to work with SauceNAO locally',
      url='https://github.com/DaRealFreak/saucenao',
      author='DaRealFreak',
      author_email='steffen.keuper@web.de',
      license='MIT',
      install_requires=[
          'Pillow',
          'bs4',
          'requests',
          'python-dotenv'
      ],
      zip_safe=True)
