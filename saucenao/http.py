#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import requests

from saucenao.exceptions import *

PREVIOUS_STATUS_CODE = None

STATUS_CODE_OK = 1
STATUS_CODE_SKIP = 2
STATUS_CODE_REPEAT = 3


def verify_status_code(request_response: requests.Response, file_name: str) -> tuple:
    """Verify the status code of the post request to the search url and raise exceptions if the code is unexpected

    :type request_response: requests.Response
    :type file_name: str
    :return:
    """
    if request_response.status_code == 200:
        return STATUS_CODE_OK, ''

    elif request_response.status_code == 429:
        if 'user\'s rate limit' in request_response.text:
            msg = "Search rate limit reached"
            return STATUS_CODE_REPEAT, msg
        if 'limit of 150 searches' in request_response.text:
            raise DailyLimitReachedException('Daily search limit for unregistered users reached')
        elif 'limit of 300 searches' in request_response.text:
            raise DailyLimitReachedException('Daily search limit for basic users reached')
        else:
            raise DailyLimitReachedException('Daily search limit reached')
    elif request_response.status_code == 403:
        raise InvalidOrWrongApiKeyException("Invalid or wrong API key")
    elif request_response.status_code == 413:
        msg = "Payload too large, skipping file: {0:s}".format(file_name)
        return STATUS_CODE_SKIP, msg
    else:
        msg = "Unknown status code: {0:d}".format(request_response.status_code)
        return STATUS_CODE_REPEAT, msg
