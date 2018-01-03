#!/usr/bin/python
# -*- coding: utf-8 -*-


class DailyLimitReachedException(Exception):
    pass


class InvalidOrWrongApiKeyException(Exception):
    pass


class UnknownStatusCodeException(Exception):
    pass
