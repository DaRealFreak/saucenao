#!/usr/bin/python
# -*- coding: utf-8 -*-
import io
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

    def test_check_file_object(self):
        """Test the run_application function

        :return:
        """
        # check returned object from file open
        with open(self.generate_small_jpg(), "rb") as test_file:
            results = self.saucenao.check_file_object(test_file)
            self.assertIsInstance(results, list)
            print(results)

        # check io.BytesIO object
        results = self.saucenao.check_file_object(
            io.BytesIO(
                b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52\x00\x00\x01\x00\x00\x00\x01\x00"
                b"\x01\x03\x00\x00\x00\x66\xBC\x3A\x25\x00\x00\x00\x03\x50\x4C\x54\x45\xB5\xD0\xD0\x63\x04\x16\xEA"
                b"\x00\x00\x00\x1F\x49\x44\x41\x54\x68\x81\xED\xC1\x01\x0D\x00\x00\x00\xC2\xA0\xF7\x4F\x6D\x0E\x37"
                b"\xA0\x00\x00\x00\x00\x00\x00\x00\x00\xBE\x0D\x21\x00\x00\x01\x9A\x60\xE1\xD5\x00\x00\x00\x00\x49"
                b"\x45\x4E\x44\xAE\x42\x60\x82"
            )
        )
        self.assertIsInstance(results, list)
        print(results)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceNao)
    unittest.TextTestRunner(verbosity=2).run(suite)
