#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import os.path
import re
import time
from HTMLParser import HTMLParser
# noinspection PyProtectedMember
from mimetypes import MimeTypes

import requests
from bs4 import BeautifulSoup as Soup
from bs4 import element


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
            return FileHandler.ensure_unicode(HTMLParser().unescape(text))
        if isinstance(text, str):
            text = text.decode('utf8')
        return unicode(text)

    @staticmethod
    def unicode_translate(text, chars=u"", replacement=u""):
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


class SauceNao(object):
    """"
    small script to work with SauceNao locally
    """

    SEARCH_POST_URL = 'http://saucenao.com/search.php'

    # basic account allows currently 20 images within 30 seconds
    # you can increase this value is you have a premium account
    LIMIT_30_SECONDS = 20

    # 0=html, 2=json but json is omitting important data but includes more data about authors
    # ToDo: add option to merge both results
    OUTPUT_TYPE = 0

    directory = None
    mime = None

    def __init__(self, directory):
        """
        initializing function

        :param directory:
        """
        self.directory = directory
        self.mime = MimeTypes()

        files = FileHandler.get_files(directory)
        for file_name in files:
            start_time = time.time()
            result_html = self.check_image(file_name)
            sorted_results = self.parse_results_json(result_html, file_name)

            from pprint import pprint
            pprint(sorted_results)

            duration = time.time() - start_time
            if duration < (30 / self.LIMIT_30_SECONDS):
                logger.debug("sleeping '{:.2f}' seconds".format((30 / self.LIMIT_30_SECONDS) - duration))
                time.sleep((30 / self.LIMIT_30_SECONDS) - duration)

    def check_image(self, file_name):
        """
        check the possible sources for the given file

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
            'output_type': self.OUTPUT_TYPE,
            'db': args.databases,
        }

        if args.api_key:
            params['api_key'] = args.api_key

        link = requests.post(url=self.SEARCH_POST_URL, files=files, params=params, headers=headers)

        if self.OUTPUT_TYPE == 0:
            return self.parse_results_html_to_json(link.text)

        return link.text

    @staticmethod
    def parse_results_html_to_json(html):
        """
        parse the results and sort them descending by similarity

        :param html:
        :return:
        """
        soup = Soup(html, 'html.parser')
        # basic format of json API response
        results = {'header': {}, 'results': []}

        for res in soup.find_all('td', attrs={"class": "resulttablecontent"}):  # type: element.Tag
            title = res.find_next('div', attrs={"class": "resulttitle"}).text
            similarity = res.find_next('div', attrs={"class": "resultsimilarityinfo"}).text.replace('%', '')
            alternate_links = [a_tag['href'] for a_tag in
                               res.find_next('div', attrs={"class": "resultmiscinfo"}).find_all('a', href=True)]
            content_column_tag = res.find_next('div', attrs={"class": "resultcontentcolumn"})
            for br in content_column_tag.find_all("br"):
                br.replace_with("\n")
            content_column = content_column_tag.text

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
    def parse_results_json(text, file_name):
        """
        parse the results and sort them descending by similarity

        :param text:
        :param file_name:
        :return:
        """
        result = json.loads(text)

        if not result['results']:
            logger.info('No results found for image: {0:s}'.format(file_name))

        results = [res for res in result['results']]
        return sorted(results, key=lambda k: float(k['header']['similarity']), reverse=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='directory to sort', required=True)
    parser.add_argument('-db', '--databases', default=999, type=int, help='which databases should be searched')
    parser.add_argument('-m', '--minimum-match', default=65, type=int, help='minimum similarity percentage')
    parser.add_argument('-k', '--api-key', help='API key of your account on saucenao')
    parser.add_argument('-x', '--exclude-categories', type=str, help='exclude specific categories from moving')
    parser.add_argument('-mv', '--move-to-categories', default=False, type=bool, help='move images to categories')
    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)

    SauceNao(args.dir)
