#!/usr/bin/python
# -*- coding: utf-8 -*-
import html
import os
import re
from shutil import move
from typing import Generator

from saucenao.files.filter import Filter


class FileHandler:
    @staticmethod
    def get_files(directory, file_filter=None) -> Generator[str, None, None]:
        """Get all files from given directory

        :type directory: str
        :type file_filter: Filter
        :return:
        """
        if file_filter:
            for f in file_filter.apply(directory=directory):
                yield f
        else:
            for f in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, f)):
                    yield f

    @staticmethod
    def unicode_translate(text, chars="", replacement="") -> str:
        """Replacement for the string.maketrans function

        :type text: str
        :type chars: str
        :type replacement: str
        :return:
        """
        for char in chars:
            text = text.replace(char, replacement[chars.index(char)])
        return text

    @staticmethod
    def move_to_category(filename, category, base_directory=os.getcwd()):
        """Move file to the sub_category folder

        :type base_directory: str
        :type filename: str
        :type category: str
        :return:
        """
        folder = re.sub(r'["/?*:<>|]', r'', html.unescape(category))
        folder = os.path.join(base_directory, folder)
        folder = os.path.abspath(FileHandler.unicode_translate(folder, "\n\t\r", "   "))
        if not os.path.exists(folder):
            os.makedirs(folder)
        move(os.path.join(base_directory, filename), os.path.join(folder, filename))
