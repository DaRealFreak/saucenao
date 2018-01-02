#!/usr/bin/python
# -*- coding: utf-8 -*-
import html
import os
import re
from shutil import move


class FileHandler:
    def __init__(self):
        """
        initializing function
        """
        pass

    @staticmethod
    def get_files(directory):
        """
        get all files from given directory

        :param directory:
        :return:
        """
        for f in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, f)):
                yield f

    @staticmethod
    def ensure_unicode(text):
        """
        ensure unicode encoding

        :param text:
        :return:
        """
        if re.match(r'.*&#[\d]{2,6};.*', text):
            return FileHandler.ensure_unicode(html.unescape(text))
        if isinstance(text, str):
            text = text.decode('utf8')
        return str(text)

    @staticmethod
    def unicode_translate(text, chars="", replacement=""):
        """
        replacement for the string.maketrans function

        :param text:
        :param chars:
        :param replacement:
        :return:
        """
        for char in chars:
            text = text.replace(char, replacement[chars.index(char)])
        return text

    @staticmethod
    def move_to_category(filename, category, base_directory=''):
        """
        move file to the sub_category folder

        :param base_directory:
        :param filename:
        :param category:
        :return:
        """
        folder = FileHandler.ensure_unicode(re.sub(r'["/?*:<>|]', r'', category))
        folder = os.path.join(base_directory, folder)
        folder = os.path.abspath(FileHandler.unicode_translate(folder, "\n\t\r", "   "))
        if not os.path.exists(folder):
            os.makedirs(folder)
        move(os.path.join(base_directory, filename), os.path.join(folder, filename))
