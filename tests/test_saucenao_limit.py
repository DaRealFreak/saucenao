#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import unittest
import uuid

import dotenv
from PIL import Image

from saucenao.saucenao import DailyLimitReachedException
from saucenao.saucenao import SauceNao

dotenv_path = os.path.join(os.path.dirname(__file__), os.pardir, '.env')
dotenv.load_dotenv(dotenv_path)

SAUCENAO_MIN_WIDTH = 3
SAUCENAO_MIN_HEIGHT = 3

SAUCENAO_IP_LIMIT = 300
SAUCENAO_API_KEY = os.environ.get('SAUCENAO_API_KEY')


def generate_small_jpg():
    """
    generate a rather small jpg file to upload faster(631 bytes)

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
        """
        constructor for the unittest

        :return:
        """
        self.test_jpg = generate_small_jpg()
        self.saucenao_html = SauceNao(os.getcwd(), output_type=SauceNao.API_HTML_TYPE)
        self.saucenao_json = SauceNao(os.getcwd(), output_type=SauceNao.API_JSON_TYPE)
        self.tests_order = [
            self.check_response_no_api_key,
            self.check_response_api_key,
        ]

    def tearDown(self):
        """
        destructor for the unittest

        :return:
        """
        os.remove(self.test_jpg)

    def run_tests(self, saucenao, success):
        """
        run the different tests with the given SauceNao instance

        :param saucenao:
        :param success:
        :return:
        """
        for test in self.tests_order:
            try:
                test(saucenao, assert_success=success)
            except Exception as e:
                self.fail("{} failed ({}: {})".format(test, type(e), e))

    def test_limits(self):
        """
        test the limits of SauceNAO

        :return:
        """
        self.run_tests(saucenao=self.saucenao_html, success=True)
        self.run_tests(saucenao=self.saucenao_json, success=True)

        # now reach the daily limit
        test_files = [self.test_jpg] * (SAUCENAO_IP_LIMIT - 2)
        try:
            # check_files returns a generator so we have to improvise here a bit
            for _ in self.saucenao_html.check_files(test_files):
                pass
        except DailyLimitReachedException:
            pass

        self.run_tests(saucenao=self.saucenao_html, success=False)
        self.run_tests(saucenao=self.saucenao_json, success=False)

    def check_response_no_api_key(self, saucenao, assert_success=True):
        """
        check the response without an API key
        on assert_success=True expect a dictionary, else an exception

        :param saucenao:
        :param assert_success:
        :return:
        """
        if assert_success:
            result = saucenao.check_file(self.test_jpg)
            self.assertIsInstance(result, list)
        else:
            self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)

    def check_response_api_key(self, saucenao, assert_success=True):
        """
        check the response with an API key
        on assert_success=True expect a dictionary, else an exception

        :param saucenao:
        :param assert_success:
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
