#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import re
import shutil
import unittest
import uuid
from stat import ST_MTIME, ST_ATIME
from time import time, sleep

from saucenao.files.constraint import Constraint
from saucenao.files.filter import Filter


class TestFilesFilter(unittest.TestCase):
    """
    test cases for the filter in the files submodule
    """

    TEST_BIG_FILE_SIZE = 1024

    def setUp(self):
        """Constructor for the unittest

        :return:
        """
        self.dir = os.path.join(os.getcwd(), str(uuid.uuid4()))
        os.mkdir(self.dir)
        self.create_test_dir()
        # no files found for this time
        self.time_before_first_creation = time()
        sleep(0.1)
        self.create_big_file()
        # 1 file found
        self.time_after_first_creation = time()
        self.create_named_file()
        # we set the last modified time to 4 hours in the future, add a second
        # to get rid of other file operations
        self.time_modifying = time()
        self.create_modified_file()
        # wait for file operations to finish
        sleep(0.2)

    def tearDown(self):
        """Destructor for the unittest

        :return:
        """
        shutil.rmtree(self.dir)

    def test_files(self):
        """Test for files no folders

        :return:
        """
        expected_file_count = len([f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))])
        file_filter = Filter(assert_is_file=True)
        file_count = len(list(file_filter.apply(self.dir)))
        self.assertTrue(expected_file_count == file_count)

    def test_folders(self):
        """Test for folders no files

        :return:
        """
        expected_folder_count = len([f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))])
        folder_filter = Filter(assert_is_folder=True)
        folder_count = len(list(folder_filter.apply(self.dir)))
        self.assertTrue(folder_count == expected_folder_count)

    def test_named_file(self):
        """Test for regex match

        :return:
        """

        def test_cmp(value, expected_value):
            return expected_value.match(value)

        # check if we have more than just 1 file in the directory
        self.assertTrue(len(os.listdir(self.dir)) > 1)
        # filter now for files >= 1024 bytes
        file_filter = Filter(name=Constraint(re.compile('named*'), cmp_func=test_cmp))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 1)

    def test_modified_file(self):
        """Test for modified file

        :return:
        """
        date_string = datetime.datetime.fromtimestamp(self.time_modifying).strftime('%d.%m.%Y %H:%M:%S')

        # get files created before or at the same time
        file_filter = Filter(
            modified_date=Constraint(date_string, cmp_func=Constraint.cmp_value_smaller_or_equal))
        files = file_filter.apply(directory=self.dir)
        len_files_before_modified_date = len(list(files))

        # get files modified after last file got created
        file_filter = Filter(
            modified_date=Constraint(date_string, cmp_func=Constraint.cmp_value_bigger))
        files = file_filter.apply(directory=self.dir)
        len_files_after_modified_date = len(list(files))

        self.assertTrue(len_files_after_modified_date == 1)
        self.assertTrue(len_files_before_modified_date > len_files_after_modified_date)

    def test_big_file(self):
        """Test for file size filter

        :return:
        """
        # check if we have more than just 1 file in the directory
        self.assertTrue(len(os.listdir(self.dir)) > 1)
        # filter now for files >= 1024 bytes
        file_filter = Filter(size=Constraint(self.TEST_BIG_FILE_SIZE, cmp_func=Constraint.cmp_value_bigger_or_equal))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 1)

    def create_big_file(self):
        """Create a file with a fixed size

        :return:
        """
        file_name = os.path.join(self.dir, str(uuid.uuid4()))
        with open(file_name, "wb") as file_handler:
            file_handler.seek(self.TEST_BIG_FILE_SIZE - 1)
            file_handler.write(b"\0")

    def create_named_file(self):
        """Create a file with a specific name

        :return:
        """
        file_name = os.path.join(self.dir, 'named_file')
        with open(file_name, "wb") as _:
            pass

    def create_modified_file(self):
        """Create a file and change the modification date

        :return:
        """
        file_name = os.path.join(self.dir, str(uuid.uuid4()))
        # create the file
        with open(file_name, "wb") as file_handler:
            file_handler.write(b"\0")

        st = os.stat(file_name)
        access_time = st[ST_ATIME]
        modified_time = st[ST_MTIME]

        os.utime(file_name, (access_time, modified_time + (4 * 3600)))

    def create_test_dir(self):
        """Create a subfolder for testing the folder amount

        :return:
        """
        dir_path = os.path.join(self.dir, str(uuid.uuid4()))
        os.mkdir(dir_path)


suite = unittest.TestLoader().loadTestsFromTestCase(TestFilesFilter)
unittest.TextTestRunner(verbosity=2).run(suite)
