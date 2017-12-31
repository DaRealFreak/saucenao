#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example usage

from pprint import pprint

from saucenao import run_application

if __name__ == '__main__':
    results = run_application()
    # if argument move_to_categories is set we don't get a return type, else a generator object
    if results:
        for result in results:
            pprint(result)
