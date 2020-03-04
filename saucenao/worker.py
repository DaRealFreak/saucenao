#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

try:
    from titlesearch import get_similar_titles
except ImportError:
    get_similar_titles = None

from saucenao import SauceNao, FileHandler


class Worker(SauceNao):
    """
    Worker class for checking a list of files
    """

    def __init__(self, files, *args, **kwargs):
        """
        initializing function

        :type files: list|tuple|Generator
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.complete_file_list = files

    def run(self):
        """Check all files with SauceNao and execute the specified tasks

        :return:
        """
        for file_name in self.files:
            start_time = time.time()

            filtered_results = self.check_file(file_name)

            if not filtered_results:
                self.logger.info('No results found for image: {0:s}'.format(file_name))
                continue

            if self.move_to_categories:
                self.__move_to_categories(file_name=file_name, results=filtered_results)
            else:
                yield {
                    'filename': file_name,
                    'results': filtered_results
                }

            duration = time.time() - start_time
            if duration < (30 / self.search_limit_30s):
                self.logger.debug("sleeping '{:.2f}' seconds".format((30 / self.search_limit_30s) - duration))
                time.sleep((30 / self.search_limit_30s) - duration)

    @property
    def excludes(self):
        """Property for excludes

        :return:
        """
        if self.exclude_categories:
            return [category.lower() for category in self.exclude_categories.split(",")]
        else:
            return []

    @property
    def files(self):
        """Property for files

        :return:
        """
        if self.start_file:
            # change files from generator to list
            files = list(self.complete_file_list)
            try:
                return files[files.index(self.start_file):]
            except ValueError:
                return self.complete_file_list
        return self.complete_file_list

    def __get_category(self, results):
        """retrieve the category of the checked image based which can be either
        the content of the image or the author of the image

        :param results:
        :return: str
        """
        if self.use_author_as_category:
            categories = self.get_title_value(results, SauceNao.CONTENT_AUTHOR_KEY)
        else:
            categories = self.get_content_value(results, SauceNao.CONTENT_CATEGORY_KEY)

        if not categories:
            return ''

        self.logger.debug('categories: {0:s}'.format(', '.join(categories)))

        # since many pictures are tagged as original and with a proper category
        # we remove the original category if we have more than 1 category
        if not self.use_author_as_category and len(categories) > 1 and 'original' in categories:
            categories.remove('original')

        # take the first category
        return categories[0]

    def __move_to_categories(self, file_name: str, results):
        """Check the file for categories and move it to the corresponding folder

        :type file_name: str
        :type results: list|tuple|Generator
        :return: bool
        """
        category = self.__get_category(results)
        if not category:
            self.logger.info("no categories found for file: {0:s}".format(file_name))
            return False

        if not self.use_author_as_category:
            category = self.__get_similar_title(category)

        # sub categories we don't want to move like original etc
        if category.lower() in self.excludes:
            self.logger.info("skipping excluded category: {0:s} ({1:s})".format(category, file_name))
            return False

        self.logger.info("moving {0:s} to category: {1:s}".format(file_name, category))
        FileHandler.move_to_category(file_name, category, base_directory=self.directory)
        return True

    def __get_similar_title(self, category: str):
        """Check for a similar title of the category using my TitleSearch project which you can find here:
        https://github.com/DaRealFreak/TitleSearch

        :param category:
        :return:
        """
        if get_similar_titles:
            similar_titles = get_similar_titles(category)

            if similar_titles and similar_titles[0]['similarity'] * 100 >= self.title_minimum_similarity:
                self.logger.info(
                    "Similar title found: {0:s}, {1:s} ({2:.2f}%)".format(
                        category, similar_titles[0]['title'], similar_titles[0]['similarity'] * 100))
                return similar_titles[0]['title']

        return category
