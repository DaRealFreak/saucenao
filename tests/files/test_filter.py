#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import math
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
        # set regular expression constraint
        file_filter = Filter(name=Constraint(re.compile('named*'), cmp_func=test_cmp))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 1)

    def test_extension_file(self):
        """Test filter for file extension

        :return:
        """

        def test_cmp(value, expected_value):
            return value in expected_value

        # we named our named file: named_file.jpg
        file_filter = Filter(file_type=Constraint([".png"], cmp_func=test_cmp))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 0)

        file_filter = Filter(file_type=Constraint([".jpg", ".png"], cmp_func=test_cmp))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 1)

    def test_creation_date(self):
        """Test for filtering after creation date

        :return:
        """
        date_string = datetime.datetime.fromtimestamp(self.time_modifying).strftime('%d.%m.%Y %H:%M')
        file_filter = Filter(
            creation_date=Constraint(date_string, cmp_func=Constraint.cmp_value_bigger_or_equal))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 4)
        file_filter = Filter(
            creation_date=Constraint(date_string, cmp_func=Constraint.cmp_value_smaller))
        files = file_filter.apply(directory=self.dir)
        self.assertEqual(len(list(files)), 0)

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
        file_list = list(files)
        # workaround since scrutinizer has another file in created directories with differencing sizes each run
        # normal check would've been to check the file list length == 1
        self.assertTrue('big_file' in file_list and 'named_file.jpg' not in file_list)

    def test_non_existent_path(self):
        """Test filter for removing non existent files

        :return:
        """
        file_filter = Filter()
        files = list(file_filter.apply(directory=self.dir, file_system_objects=['not-existent-file']))
        self.assertEqual(files, [])

    def test_empty_filter(self):
        """Test empty filter

        :return:
        """
        file_filter = Filter()
        files = list(file_filter.apply())
        self.assertEqual(files, [])

    def test_get_timestamp_from_datestring(self):
        """Test for date string to timestamp conversion

        :return:
        """
        # since I don't like timezones in programming, I'll just expect a returned floating type value
        self.assertIsInstance(Filter._get_timestamp_from_datestring("01.01.2017 12:45:45"), float)
        self.assertIsInstance(Filter._get_timestamp_from_datestring("01.01.2017 12:45"), float)
        self.assertIsInstance(Filter._get_timestamp_from_datestring("01.01.2017"), float)
        with self.assertRaises(AttributeError) as _:
            Filter._get_timestamp_from_datestring("this is no time string")

    def create_big_file(self):
        """Create a file with a fixed size

        :return:
        """
        file_name = os.path.join(self.dir, 'big_file')
        with open(file_name, "wb") as file_handler:
            file_handler.seek(self.TEST_BIG_FILE_SIZE - 1)
            file_handler.write(b"\0")

    def create_named_file(self):
        """Create a file with a specific name

        :return:
        """
        file_name = os.path.join(self.dir, 'named_file.jpg')
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFilesFilter)
    unittest.TextTestRunner(verbosity=2).run(suite)
