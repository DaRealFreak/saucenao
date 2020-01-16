#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import unittest
import uuid

import dotenv
from PIL import Image

from saucenao.saucenao import DailyLimitReachedException
from saucenao.saucenao import SauceNao

dotenv_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, '.env')
dotenv.load_dotenv(dotenv_path)

SAUCENAO_MIN_WIDTH = 3
SAUCENAO_MIN_HEIGHT = 3

SAUCENAO_IP_LIMIT_UNREGISTERED_USER = 150
SAUCENAO_IP_LIMIT_BASIC_USER = 300

SAUCENAO_API_KEY = os.environ.get('SAUCENAO_API_KEY')


def generate_small_jpg():
    """Generate a rather small jpg file to upload faster(631 bytes)

    :return:
    """
    file_path = str(uuid.uuid4()) + ".jpg"
    im = Image.new("RGB", (SAUCENAO_MIN_WIDTH, SAUCENAO_MIN_HEIGHT))
    im.save(os.path.join(os.getcwd(), file_path), "JPEG")
    return file_path


class TestSauceNaoLimits(unittest.TestCase):
    """
    test cases to check the limits for SauceNAO

    currently not covered is the test case: account limit reached, ip limit not reached
    have to add a proxy for this test case to be covered.

    Test cases covered:
     - HTML response type: ip/account limit not reached
     - JSON response type: ip/account limit not reached
     - HTML response type: ip limit reached
     - JSON response type: ip limit reached
    """

    def setUp(self):
        """Constructor for the unittest

        :return:
        """
        self.test_jpg = generate_small_jpg()

        self.saucenao_html = SauceNao(os.getcwd(), output_type=SauceNao.API_HTML_TYPE, log_level=logging.DEBUG)
        self.saucenao_json = SauceNao(os.getcwd(), output_type=SauceNao.API_JSON_TYPE, log_level=logging.DEBUG)

        self.NOT_IP_LIMIT_NOT_ACCOUNT_LIMIT = [
            {'function': self.check_response_no_api_key, 'expected_success': True},
            {'function': self.check_response_api_key, 'expected_success': True}
        ]
        self.IP_LIMIT_NOT_ACCOUNT_LIMIT = [
            {'function': self.check_response_no_api_key, 'expected_success': False},
            {'function': self.check_response_api_key, 'expected_success': True}
        ]
        self.IP_LIMIT_ACCOUNT_LIMIT = [
            {'function': self.check_response_no_api_key, 'expected_success': False},
            {'function': self.check_response_api_key, 'expected_success': False}
        ]

    def tearDown(self):
        """Destructor for the unittest

        :return:
        """
        os.remove(self.test_jpg)

    def run_tests(self, saucenao: SauceNao, tests):
        """Run the different tests with the given SauceNao instance

        :type saucenao: SauceNao
        :type tests: list|tuple|Generator
        :return:
        """
        for test in tests:
            test_function = test['function']
            test_result = test['expected_success']
            try:
                test_function(saucenao, assert_success=test_result)
            except Exception as e:
                self.fail("{} failed ({}: {})".format(test, type(e), e))

    def test_limits(self):
        """Test the limits of SauceNAO

        :return:
        """
        self.saucenao_html.logger.info('running HTML test, ip limit not reached, account limit not reached')
        self.run_tests(saucenao=self.saucenao_html, tests=self.NOT_IP_LIMIT_NOT_ACCOUNT_LIMIT)
        self.saucenao_html.logger.info('running JSON test, ip limit not reached, account limit not reached')
        self.run_tests(saucenao=self.saucenao_json, tests=self.NOT_IP_LIMIT_NOT_ACCOUNT_LIMIT)

        # now reach the daily limit without API key to reach the IP limit
        if self.saucenao_html.api_key:
            self.saucenao_html.api_key = None

        test_files = [self.test_jpg] * (SAUCENAO_IP_LIMIT_UNREGISTERED_USER - 2)
        try:
            # check_files returns a generator so we have to improvise here a bit
            for test_file in test_files:
                self.saucenao_html.check_file(test_file)
        except DailyLimitReachedException:
            pass

        # we are at 150 searches -> IP limit unregistered user reached, not basic user
        self.saucenao_html.logger.info('running HTML test, ip limit reached, account limit not reached')
        self.run_tests(saucenao=self.saucenao_html, tests=self.IP_LIMIT_NOT_ACCOUNT_LIMIT)
        self.saucenao_html.logger.info('running JSON test, ip limit reached, account limit not reached')
        self.run_tests(saucenao=self.saucenao_json, tests=self.IP_LIMIT_NOT_ACCOUNT_LIMIT)

        # set API key to reach the account limit
        self.saucenao_html.api_key = SAUCENAO_API_KEY
        test_files = [self.test_jpg] * (SAUCENAO_IP_LIMIT_BASIC_USER - SAUCENAO_IP_LIMIT_UNREGISTERED_USER - 4)
        try:
            # check_files returns a generator so we have to improvise here a bit
            for test_file in test_files:
                self.saucenao_html.check_file(test_file)
        except DailyLimitReachedException:
            pass

        # we are at 30 searches -> IP limit basic user reached
        self.saucenao_html.logger.info('running HTML test, ip limit reached, account limit reached')
        self.run_tests(saucenao=self.saucenao_html, tests=self.IP_LIMIT_ACCOUNT_LIMIT)
        self.saucenao_html.logger.info('running JSON test, ip limit reached, account limit reached')
        self.run_tests(saucenao=self.saucenao_json, tests=self.IP_LIMIT_ACCOUNT_LIMIT)

    def check_response_no_api_key(self, saucenao: SauceNao, assert_success=True):
        """Check the response without an API key
        on assert_success=True expect a dictionary, else an exception

        :type saucenao: SauceNao
        :type assert_success: bool
        :return:
        """
        if assert_success:
            result = saucenao.check_file(self.test_jpg)
            self.assertIsInstance(result, list)
        else:
            self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)

    def check_response_api_key(self, saucenao: SauceNao, assert_success=True):
        """Check the response with an API key
        on assert_success=True expect a dictionary, else an exception

        :type saucenao: SauceNao
        :type assert_success: bool
        :return:
        """
        saucenao.api_key = SAUCENAO_API_KEY
        if assert_success:
            result = saucenao.check_file(self.test_jpg)
            self.assertIsInstance(result, list)
        else:
            self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)


suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceNaoLimits)
unittest.TextTestRunner(verbosity=2).run(suite)
