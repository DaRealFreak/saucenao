#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import types
import unittest
from uuid import uuid4

from PIL import Image

from saucenao import run_application


class TestInit(unittest.TestCase):
    SAUCENAO_MIN_WIDTH = 3
    SAUCENAO_MIN_HEIGHT = 3

    def setUp(self):
        """Constructor for unittest classes

        :return:
        """
        directory = str(uuid4())
        os.mkdir(directory)
        self.directory = os.path.abspath(directory)
        self.generate_small_jpg()

    def tearDown(self):
        """Destructor for unittest classes

        :return:
        """
        shutil.rmtree(self.directory)

    def generate_small_jpg(self):
        """Generate a rather small jpg file to upload faster(631 bytes)

        :return:
        """
        file_path = str(uuid4()) + ".jpg"
        im = Image.new("RGB", (self.SAUCENAO_MIN_WIDTH, self.SAUCENAO_MIN_HEIGHT))
        im.save(os.path.join(self.directory, file_path), "JPEG")
        return file_path

    def test_run_application(self):
        """Test the run_application function

        :return:
        """
        sys.argv = [sys.argv[0], '-d', self.directory]
        results = run_application()
        self.assertIsInstance(results, types.GeneratorType)
        results = list(results)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    unittest.TextTestRunner(verbosity=2).run(suite)
