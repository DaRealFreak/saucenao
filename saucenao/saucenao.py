#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import logging
import os
import os.path
import re
import time
# noinspection PyProtectedMember
from mimetypes import MimeTypes

import requests
from bs4 import BeautifulSoup as Soup
from bs4 import element

from .exceptions import *
from .filehandler import FileHandler


class SauceNao(object):
    """"
    small script to work with SauceNao locally
    """

    SEARCH_POST_URL = 'http://saucenao.com/search.php'

    # basic account allows currently 20 images within 30 seconds
    # you can increase this value is you have a premium account
    LIMIT_30_SECONDS = 20

    # 0=html, 2=json but json is omitting important data but includes more data about authors
    # taken from the API documentation(requires login): https://saucenao.com/user.php?page=search-api
    API_HTML_TYPE = 0
    API_JSON_TYPE = 2

    CONTENT_CATEGORY_KEY = 'Material'
    CONTENT_CHARACTERS_KEY = 'Characters'

    directory = None
    mime = None

    def __init__(self, directory, databases=999, minimum_similarity=65, combine_api_types=False, api_key=None,
                 exclude_categories='', move_to_categories=False, output_type=API_HTML_TYPE, start_file=None,
                 log_level=logging.ERROR):
        """
        initializing function

        :param directory:
        :param databases:
        :param minimum_similarity:
        :param combine_api_types:
        :param api_key:
        :param exclude_categories:
        :param move_to_categories:
        :param start_file:
        :param log_level:
        """
        self.directory = directory
        self.databases = databases
        self.minimum_similarity = minimum_similarity
        self.combine_api_types = combine_api_types
        self.api_key = api_key
        self.exclude_categories = exclude_categories
        self.move_to_categories = move_to_categories
        self.output_type = output_type
        self.start_file = start_file

        self.mime = MimeTypes()
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger("saucenao_logger")

    def check_files(self, files):
        """
        check all files with SauceNao and execute the specified tasks

        :type files: list
        :param files:
        :return:
        """
        if self.exclude_categories:
            excludes = [l.lower() for l in self.exclude_categories.split(",")]
        else:
            excludes = []

        if self.start_file:
            # change files from generator to list
            files = list(files)
            try:
                files = files[files.index(self.start_file):]
            except ValueError:
                pass

        for file_name in files:
            start_time = time.time()

            filtered_results = self.check_file(file_name)

            if not filtered_results:
                self.logger.info('No results found for image: {0:s}'.format(file_name))
                continue

            if self.move_to_categories:
                categories = self.get_content_value(filtered_results, self.CONTENT_CATEGORY_KEY)

                if not categories:
                    self.logger.info("no categories found for file: {0:s}".format(file_name))
                    continue

                self.logger.debug('categories: {0:s}'.format(', '.join(categories)))

                # since many pictures are tagged as original and with a proper category
                # we remove the original category if we have more than 1 category
                if len(categories) > 1 and 'original' in categories:
                    categories.remove('original')

                # take the first category
                category = categories[0]

                # sub categories we don't want to move like original etc
                if category.lower() in excludes:
                    self.logger.info("skipping excluded category: {0:s} ({1:s})".format(category, file_name))
                    continue

                self.logger.info("moving {0:s} to category: {1:s}".format(file_name, category))
                FileHandler.move_to_category(file_name, category, base_directory=self.directory)
            else:
                yield {
                    'filename': file_name,
                    'results': filtered_results
                }

            duration = time.time() - start_time
            if duration < (30 / self.LIMIT_30_SECONDS):
                self.logger.debug("sleeping '{:.2f}' seconds".format((30 / self.LIMIT_30_SECONDS) - duration))
                time.sleep((30 / self.LIMIT_30_SECONDS) - duration)

    def check_file(self, file_name):
        """
        check the given file for results on SauceNAO

        :param file_name:
        :return:
        """
        if self.combine_api_types:
            result = self.check_image(file_name, self.API_HTML_TYPE)
            sorted_results = self.parse_results_json(result)

            additional_result = self.check_image(file_name, self.API_JSON_TYPE)
            additional_sorted_results = self.parse_results_json(additional_result)
            sorted_results = self.merge_results(sorted_results, additional_sorted_results)
        else:
            result = self.check_image(file_name, self.output_type)
            sorted_results = self.parse_results_json(result)

        filtered_results = self.filter_results(sorted_results)
        return filtered_results

    def check_image(self, file_name, output_type):
        """
        check the possible sources for the given file

        :type output_type: int
        :type file_name: str
        :param output_type:
        :param file_name:
        :return:
        """
        file_path = os.path.join(self.directory, file_name)

        files = {'file': open(file_path, 'rb').read()}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/63.0.3239.84 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-DE,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        params = {
            'file': file_path,
            'Content-Type': self.mime.guess_type(file_path),
            # parameters taken from form on main page: https://saucenao.com/
            'url': None,
            'frame': 1,
            'hide': 0,
            # parameters taken from API documentation: https://saucenao.com/user.php?page=search-api
            'output_type': output_type,
            'db': self.databases,
        }

        if self.api_key:
            params['api_key'] = self.api_key

        link = requests.post(url=self.SEARCH_POST_URL, files=files, params=params, headers=headers)

        if link.status_code != 200:
            if link.status_code == 429:
                if 'limit of 150 searches' in link.text:
                    self.logger.error("Daily search limit for unregistered users reached")
                    raise DailyLimitReachedException('Daily search limit for unregistered users reached')
                if 'limit of 300 searches' in link.text:
                    self.logger.error("Daily search limit for basic users reached")
                    raise DailyLimitReachedException('Daily search limit for basic users reached')
                else:
                    self.logger.error("Daily search limit reached")
                    raise DailyLimitReachedException('Daily search limit reached')
            if link.status_code == 403:
                self.logger.error("Invalid or wrong API key")
                raise InvalidOrWrongApiKeyException("Invalid or wrong API key")
            else:
                self.logger.error("Unknown status code: {0:d}".format(link.status_code))
                raise UnknownStatusCodeException("Unknown status code: {0:d}".format(link.status_code))

        if output_type == self.API_HTML_TYPE:
            return self.parse_results_html_to_json(link.text)

        return link.text

    @staticmethod
    def parse_results_html_to_json(html):
        """
        parse the results and sort them descending by similarity

        :type html: str
        :param html:
        :return:
        """
        soup = Soup(html, 'html.parser')
        # basic format of json API response
        results = {'header': {}, 'results': []}

        for res in soup.find_all('td', attrs={"class": "resulttablecontent"}):  # type: element.Tag
            # optional field in SauceNao
            title_tag = res.find_next('div', attrs={"class": "resulttitle"})
            if title_tag:
                title = title_tag.text
            else:
                title = ''

            # mandatory field in SauceNao
            similarity = res.find_next('div', attrs={"class": "resultsimilarityinfo"}).text.replace('%', '')
            alternate_links = [a_tag['href'] for a_tag in
                               res.find_next('div', attrs={"class": "resultmiscinfo"}).find_all('a', href=True)]
            content_column = []
            content_column_tags = res.find_all('div', attrs={"class": "resultcontentcolumn"})
            for content_column_tag in content_column_tags:
                for br in content_column_tag.find_all('br'):
                    br.replace_with('\n')
                content_column.append(content_column_tag.text)

            result = {
                'header': {
                    'similarity': similarity
                },
                'data': {
                    'title': title,
                    'content': content_column,
                    'ext_urls': alternate_links
                }
            }
            results['results'].append(result)

        return json.dumps(results)

    @staticmethod
    def parse_results_json(text):
        """
        parse the results and sort them descending by similarity

        :type text: str
        :param text:
        :return:
        """
        result = json.loads(text)
        results = [res for res in result['results']]
        return sorted(results, key=lambda k: float(k['header']['similarity']), reverse=True)

    def filter_results(self, sorted_results):
        """
        return results with a similarity bigger or the same as the defined similarity from the arguments (default 65%)

        :type sorted_results: list
        :param sorted_results:
        :return:
        """
        filtered_results = []
        for res in sorted_results:
            if float(res['header']['similarity']) >= float(self.minimum_similarity):
                filtered_results.append(res)
            else:
                # we can break here since the results are sorted by similarity anyways
                break
        return filtered_results

    @staticmethod
    def get_content_value(results, key):
        """
        return the first match of Material in content
        multiple sites have a categorisation which SauceNao utilizes to provide it in the content section

        :type results: list
        :type key: str
        :param results:
        :param key:
        :return:
        """
        for result in results:
            if 'content' in list(result['data'].keys()):
                for content in result['data']['content']:
                    if re.match('{0:s}: .*'.format(key), content):
                        return ''.join(re.split(r'{0:s}: '.format(key), content)[1:]).rstrip("\n").split('\n')
        return ''

    @staticmethod
    def merge_two_dicts(x, y):
        """
        take x dictionary and insert/overwrite y dictionary values

        :type x: dict
        :type y: dict
        :param x:
        :param y:
        :return:
        """
        z = x.copy()
        z.update(y)
        return z

    def merge_results(self, result, additional_result):
        """
        merge two result arrays

        :type result: list
        :type additional_result: list
        :param result:
        :param additional_result:
        :return:
        """
        if len(result) <= len(additional_result):
            length = len(result)
        else:
            length = len(additional_result)

        for i in range(length):
            for key in list(result[i].keys()):
                result[i][key] = self.merge_two_dicts(result[i][key], additional_result[i][key])

        return result
