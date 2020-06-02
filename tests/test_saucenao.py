#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from uuid import uuid4

from PIL import Image

from saucenao import SauceNao


class TestSauceNao(unittest.TestCase):
    SAUCENAO_MIN_WIDTH = 3
    SAUCENAO_MIN_HEIGHT = 3

    def setUp(self):
        """Constructor for unittest classes

        :return:
        """
        directory = str(uuid4())
        os.mkdir(directory)
        self.directory = os.path.abspath(directory)
        self.saucenao = SauceNao()

    def tearDown(self):
        """Destructor for unittest classes

        :return:
        """
        shutil.rmtree(self.directory)

    def generate_small_jpg(self):
        """Generate a rather small jpg file to upload faster(631 bytes)

        :return:
        """
        file_path = os.path.join(self.directory, str(uuid4()) + ".jpg")
        im = Image.new("RGB", (self.SAUCENAO_MIN_WIDTH, self.SAUCENAO_MIN_HEIGHT))
        im.save(file_path, "JPEG")
        return file_path

    def test_run_application(self):
        """Test the run_application function

        :return:
        """
        with open(self.generate_small_jpg(), "rb") as test_file:
            results = self.saucenao.check_file_object(test_file)
            self.assertIsInstance(results, list)
            print(results)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceNao)
    unittest.TextTestRunner(verbosity=2).run(suite)
