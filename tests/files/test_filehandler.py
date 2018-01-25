#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest
import uuid
from time import sleep

from saucenao import FileHandler, Filter


class TestFileHandler(unittest.TestCase):
    """
    test cases for the file handler operations
    """

    def setUp(self):
        """Constructor for the unittest

        :return:
        """
        self.dir = os.path.join(os.getcwd(), str(uuid.uuid4()))
        os.mkdir(self.dir)

        file_name = os.path.join(self.dir, str(uuid.uuid4()))
        # create a file
        with open(file_name, "wb") as _:
            pass

        # wait for file operations to finish
        sleep(0.5)

    def tearDown(self):
        """Destructor for the unittest

        :return:
        """
        shutil.rmtree(self.dir)

    def test_get_files(self):
        """Test the get_files function of the file handler

        :return:
        """
        files = FileHandler.get_files(directory=self.dir)
        self.assertEqual(len(list(files)), 1)

        file_filter = Filter(assert_is_folder=True)
        files = FileHandler.get_files(directory=self.dir, file_filter=file_filter)
        self.assertEqual(len(list(files)), 0)

        file_filter = Filter(assert_is_file=True)
        files = FileHandler.get_files(directory=self.dir, file_filter=file_filter)
        self.assertEqual(len(list(files)), 1)

    def test_move_to_category(self):
        """Test moving the file to a category folder

        :return:
        """
        files = list(FileHandler.get_files(directory=self.dir))
        self.assertEqual(len(files), 1)
        for file in files:
            FileHandler.move_to_category(file, 'Example Category', self.dir)

        new_files = FileHandler.get_files(directory=self.dir)
        self.assertEqual(len(list(new_files)), 0)
