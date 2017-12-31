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

    def setUp(self):
        """
        constructor for the unittest

        :return:
        """
        self.test_jpg = generate_small_jpg()

    def tearDown(self):
        """
        destructor for the unittest

        :return:
        """
        os.remove(self.test_jpg)

    def test_limit_html(self):
        """
        test cases for SauceNAO limits with return type html
        currently not covered: account limit reached but ip limit not reached
        not possible to cover without proxy usage

        :return:
        """
        saucenao = SauceNao(os.getcwd(), output_type=SauceNao.API_HTML_TYPE)

        # test case: ip limit not reached, no api key set
        result = saucenao.check_file(self.test_jpg)
        self.assertIsInstance(result, dict)

        # test case: ip limit not reached, api key set
        saucenao.api_key = SAUCENAO_API_KEY
        result = saucenao.check_file(self.test_jpg)
        self.assertIsInstance(result, dict)

        # now to reach the daily limit we spam the same image until we receive the exception
        saucenao.api_key = None
        test_files = [self.test_jpg] * SAUCENAO_IP_LIMIT - 2
        try:
            # check_files returns a generator so we have to improvise here a bit
            for _ in saucenao.check_files(test_files):
                pass
        except DailyLimitReachedException:
            pass

        # test case: ip limit reached, account limit not reached but api_key not set
        self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)

        # test case: ip limit reached, account limit not reached but api_key set
        saucenao.api_key = SAUCENAO_API_KEY
        self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)

    def test_limit_json(self):
        """
        test cases for SauceNAO limits with return type json
        currently not covered: account limit reached but ip limit not reached
        not possible to cover without proxy usage

        :return:
        """
        saucenao = SauceNao(os.getcwd(), output_type=SauceNao.API_JSON_TYPE)

        # test case: ip limit not reached, no api key set
        result = saucenao.check_file(self.test_jpg)
        self.assertIsInstance(result, dict)

        # test case: ip limit not reached, api key set
        saucenao.api_key = SAUCENAO_API_KEY
        result = saucenao.check_file(self.test_jpg)
        self.assertIsInstance(result, dict)

        # now to reach the daily limit we spam the same image until we receive the exception
        saucenao.api_key = None
        test_files = [self.test_jpg] * SAUCENAO_IP_LIMIT - 2
        try:
            # check_files returns a generator so we have to improvise here a bit
            for _ in saucenao.check_files(test_files):
                pass
        except DailyLimitReachedException:
            pass

        # test case: ip limit reached, account limit not reached but api_key not set
        self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)

        # test case: ip limit reached, account limit not reached but api_key set
        saucenao.api_key = SAUCENAO_API_KEY
        self.assertRaises(DailyLimitReachedException, saucenao.check_file, self.test_jpg)


suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceNaoLimits)
unittest.TextTestRunner(verbosity=2).run(suite)
