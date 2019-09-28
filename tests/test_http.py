#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

import requests_mock

from saucenao.http import *


class TestHttp(unittest.TestCase):
    """Test the verify_status_code function with multiple mock responses"""

    def setUp(self):
        """set up for unittests

        :return:
        """
        self.dummy_url = "mock://localhost"

    @requests_mock.mock()
    def test_status_code_ok(self, mock):
        """Test the verify status code function for 200 ok status code

        :return:
        """
        mock.get(self.dummy_url, status_code=200)
        status_code, msg = verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
        self.assertEqual(status_code, STATUS_CODE_OK)

    @requests_mock.mock()
    def test_status_code_skip(self, mock):
        """Test the verify status code function for 413 payload too large status code

        :return:
        """
        mock.get(self.dummy_url, status_code=413)
        status_code, msg = verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
        self.assertEqual(status_code, STATUS_CODE_SKIP)

    @requests_mock.mock()
    def test_status_code_repeat(self, mock):
        """Test the verify status code function with multiple mock request responses

        :return:
        """
        mock.get(self.dummy_url, text='', status_code=999)
        status_code, msg = verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
        self.assertEqual(status_code, STATUS_CODE_REPEAT)

    @requests_mock.mock()
    def test_status_code_api_key(self, mock):
        """Test the verify status code function for 403 wrong api key status

        :return:
        """
        mock.get(self.dummy_url, text='', status_code=403)
        with self.assertRaises(InvalidOrWrongApiKeyException) as _:
            verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')

    @requests_mock.mock()
    def test_status_code_limit(self, mock):
        """Test the verify status code function for 429 limit reached status

        :return:
        """
        mock.get(self.dummy_url, text='limit of 150 searches reached', status_code=429)
        with self.assertRaises(DailyLimitReachedException) as exception:
            verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
            self.assertEqual(str(exception), 'Daily search limit for unregistered users reached')

        mock.get(self.dummy_url, text='limit of 300 searches reached', status_code=429)
        with self.assertRaises(DailyLimitReachedException) as exception:
            verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
            self.assertEqual(str(exception), 'Daily search limit for basic users reached')

        mock.get(self.dummy_url, status_code=429)
        with self.assertRaises(DailyLimitReachedException) as exception:
            verify_status_code(request_response=requests.get(self.dummy_url), file_name='tmp')
            self.assertEqual(str(exception), 'Daily search limit reached')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHttp)
    unittest.TextTestRunner(verbosity=2).run(suite)
