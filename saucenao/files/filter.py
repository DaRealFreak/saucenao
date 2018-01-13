#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import re
from pathlib import Path
from stat import ST_CTIME, ST_MTIME, ST_SIZE
from typing import Generator

from saucenao.files.constraint import Constraint


class Filter:
    """
    Filter to apply constraints for multiple metadata entries of the files.
    Obviously the files have to exist or they'll automatically get removed.
    Returns a generator object
    """

    def __init__(self, assert_is_file=False, creation_date=None, modified_date=None, name=None, file_type=None,
                 size=None):
        """Initializing function

        :type assert_is_file: bool
        :type creation_date: Constraint
        :type modified_date: Constraint
        :type name: Constraint
        :type file_type: Constraint
        :type size: Constraint
        """
        self.filter_assert_is_file = assert_is_file
        self.filter_creation_date = creation_date
        self.filter_modified_date = modified_date
        self.filter_name = name
        self.filter_file_type = file_type
        self.filter_file_size = size

    @staticmethod
    def _get_timestamp_from_datestring(date_string):
        """Convert the given date string to timestamp

        :param date_string:
        :return:
        """
        if re.match('\d+.\d+.\d+ \d+:\d+:\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S").timestamp()
        elif re.match('\d+.\d+.\d+ \d+:\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M").timestamp()
        elif re.match('\d+.\d+.\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y").timestamp()
        else:
            raise AttributeError("The date doesn't fit the format: d.m.Y[ H:M[:S]]")

    def apply(self, file_system_objects, directory=os.getcwd()):
        """Apply the filter values to the given FSOs(File System Objects)

        :type file_system_objects: list|tuple|Generator
        :type directory: str
        :return:
        """
        for file_system_object in file_system_objects:
            abs_path = os.path.join(directory, file_system_object)

            # check if the FSO exists, else we can't access the metadata
            if not os.path.exists(abs_path):
                continue

            # check if the FSO is a file
            if self.filter_assert_is_file and not os.path.isfile(abs_path):
                continue

            file_stats = os.stat(abs_path)

            # check if the FSO creation date matches the constraint
            if self.filter_creation_date:
                creation_time = file_stats[ST_CTIME]
                expected_creation_time = self._get_timestamp_from_datestring(self.filter_creation_date.value)
                if not self.filter_creation_date.cmp_func(creation_time, expected_creation_time):
                    continue

            # check if the FSO modification date matches the constraint
            if self.filter_modified_date:
                modified_time = file_stats[ST_MTIME]
                expected_modified_time = self._get_timestamp_from_datestring(self.filter_modified_date.value)
                if not self.filter_modified_date.cmp_func(modified_time, expected_modified_time):
                    continue

            # check if the FSO name matches the constraint
            if self.filter_name:
                if not self.filter_name.cmp_func(self.filter_name.value, file_system_object):
                    continue

            # check if the FSO suffix matches the constraint
            if self.filter_file_type:
                if not self.filter_file_type.cmp_func(self.filter_file_type.value, Path(abs_path).suffix):
                    continue

            # check if the FSO size matches the constraint
            if self.filter_file_size:
                if not self.filter_file_size.cmp_func(self.filter_file_size.value, file_stats[ST_SIZE]):
                    continue

            yield file_system_object
