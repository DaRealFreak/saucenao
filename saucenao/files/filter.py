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

    _directory = None
    _file_system_objects = None

    def __init__(self, assert_is_folder=False, assert_is_file=False, creation_date=None, modified_date=None, name=None,
                 file_type=None, size=None):
        """Initializing function

        :type assert_is_folder: bool
        :type assert_is_file: bool
        :type creation_date: Constraint
        :type modified_date: Constraint
        :type name: Constraint
        :type file_type: Constraint
        :type size: Constraint
        """
        self._filter_assert_is_folder = assert_is_folder
        self._filter_assert_is_file = assert_is_file
        self._filter_creation_date = creation_date
        self._filter_modified_date = modified_date
        self._filter_name = name
        self._filter_file_type = file_type
        self._filter_file_size = size

    @property
    def file_system_objects(self):
        """Property for file system objects

        :return:
        """
        if self._file_system_objects is None:
            if self._directory:
                return os.listdir(self._directory)
            else:
                return []
        return self._file_system_objects

    @staticmethod
    def _get_timestamp_from_datestring(date_string) -> float:
        """Convert the given date string to timestamp

        :param date_string:
        :return:
        """
        if re.match(r'\d+.\d+.\d+ \d+:\d+:\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S").timestamp()
        elif re.match(r'\d+.\d+.\d+ \d+:\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M").timestamp()
        elif re.match(r'\d+.\d+.\d+', date_string):
            return datetime.datetime.strptime(date_string, "%d.%m.%Y").timestamp()
        else:
            raise AttributeError("The date doesn't fit the format: d.m.Y[ H:M[:S]]")

    def apply(self, directory='', file_system_objects=None) -> Generator[str, None, None]:
        """Apply the filter values to the given FSOs(File System Objects)

        :type directory: str
        :type file_system_objects: list|tuple|Generator
        :return:
        """
        self._directory = directory
        self._file_system_objects = file_system_objects

        for file_system_object in self.file_system_objects:
            abs_path = os.path.join(directory, file_system_object)

            # check if the FSO exists, else we can't access the metadata
            if not os.path.exists(abs_path):
                continue

            # check if the FSO is a file
            if self._filter_assert_is_file and not os.path.isfile(abs_path):
                continue

            # check if the FSO is a folder
            if self._filter_assert_is_folder and not os.path.isdir(abs_path):
                continue

            file_stats = os.stat(abs_path)

            # check if the FSO creation date matches the constraint
            if self._filter_creation_date and not self.apply_creation_date(file_stats):
                continue

            # check if the FSO modification date matches the constraint
            if self._filter_modified_date and not self.apply_modified_date(file_stats):
                continue

            # check if the FSO name matches the constraint
            if self._filter_name and not self._filter_name.cmp_func(file_system_object, self._filter_name.value):
                continue

            # check if the FSO suffix matches the constraint
            if self._filter_file_type and not self._filter_file_type.cmp_func(Path(abs_path).suffix,
                                                                              self._filter_file_type.value):
                continue

            # check if the FSO size matches the constraint
            if self._filter_file_size and not self._filter_file_size.cmp_func(file_stats[ST_SIZE],
                                                                              self._filter_file_size.value):
                continue

            yield file_system_object

    def apply_creation_date(self, file_stats: os.stat_result) -> bool:
        """Apply creation date option

        :param file_stats:
        :return:
        """
        creation_time = file_stats[ST_CTIME]
        expected_creation_time = self._get_timestamp_from_datestring(self._filter_creation_date.value)
        if self._filter_creation_date.cmp_func(creation_time, expected_creation_time):
            return True
        else:
            return False

    def apply_modified_date(self, file_stats: os.stat_result) -> bool:
        """Apply modified date option

        :param file_stats:
        :return:
        """
        modified_time = file_stats[ST_MTIME]
        expected_modified_time = self._get_timestamp_from_datestring(self._filter_modified_date.value)
        if self._filter_modified_date.cmp_func(modified_time, expected_modified_time):
            return True
        else:
            return False
