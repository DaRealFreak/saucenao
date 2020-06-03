#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from uuid import uuid4

from PIL import Image

from saucenao import Worker


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

    def test_run_worker(self):
        """Test the run_application function

        :return:
        """
        with open(self.generate_small_jpg(), "rb") as test_file:
            # test with file object and file path
            worker = Worker(files=(test_file, self.generate_small_jpg()))
            worker.run()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceNao)
    unittest.TextTestRunner(verbosity=2).run(suite)
