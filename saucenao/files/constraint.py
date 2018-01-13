#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Callable


class Constraint:

    def __init__(self, value, cmp_func: Callable):
        """Initializing function

        :param value:
        :type cmp_func: Callable
        """
        self.value = value
        self.cmp_func = cmp_func

    @staticmethod
    def cmp_value_bigger(x, y):
        return x > y

    @staticmethod
    def cmp_value_bigger_or_equal(x, y):
        return x >= y

    @staticmethod
    def cmp_value_smaller(x, y):
        return x < y

    @staticmethod
    def cmp_value_smaller_or_equal(x, y):
        return x <= y

    @staticmethod
    def cmp_value_equals(x, y):
        return x == y

    @staticmethod
    def cmp_value_not_equals(x, y):
        return x != y
