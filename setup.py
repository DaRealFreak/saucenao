#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

current_directory = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(current_directory, 'saucenao', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__description__'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      url=about['__url__'],
      author=about['__author__'],
      author_email=about['__author_email__'],
      license=about['__license__'],
      packages=find_packages(),
      install_requires=[
          'bs4>=0.0.1',
          'requests>=2.18.4'
      ],
      extras_require={
          'titlesearch': [
              'titlesearch>=0.0.1'
          ],
          'dev': [
              'python-dotenv>=0.7.1',
              'Pillow>=5.0.0',
              'requests_mock>=1.4.0',
              'nose-exclude>=0.5.0',
              'coveralls>=1.10.0'
          ]
      },
      zip_safe=True)
