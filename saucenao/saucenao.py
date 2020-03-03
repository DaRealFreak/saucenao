#!/usr/bin/python
# -*- coding: utf-8 -*-
import enum
import json
import logging
import os
import re
import time
from mimetypes import MimeTypes
from typing import Generator

import requests
from bs4 import BeautifulSoup as Soup
from bs4 import element

from saucenao import http
from saucenao.exceptions import *


class SauceNaoDatabase(enum.Enum):
    """
    database index supported by SauceNao
    """

    HMagazines = 0
    HGameCG = 2
    DoujinshiDB = 3
    PixivImages = 5
    NicoNicoSeiga = 8
    Danbooru = 9
    DrawrImages = 10
    NijieImages = 11
    YandeRe = 12
    Shutterstock = 15
    FAKKU = 16
    HMisc = 18
    TwoDMarket = 19
    MediBang = 20
    Anime = 21
    HAnime = 22
    Movies = 23
    Shows = 24
    Gelbooru = 25
    Konachan = 26
    SankakuChannel = 27
    AnimePicturesNet = 28
    E621Net = 29
    IdolComplex = 30
    BcyNetIllust = 31
    BcyNetCosplay = 32
    PortalGraphicsNet = 33
    DeviantArt = 34
    PawooNet = 35
    MadokamiManga = 36
    MangaDex = 37
    All = 999

    @classmethod
    def is_uncompleted(cls, databases):
        """Check if the database is uncompleted and the index should not be used

        :type databases: int
        :return:
        """
        return databases in [cls.HMagazines, cls.HGameCG, cls.DoujinshiDB, cls.Shutterstock, cls.Movies, cls.Shows,
                             cls.SankakuChannel, cls.IdolComplex, cls.BcyNetIllust, cls.BcyNetCosplay, cls.DeviantArt,
                             cls.PawooNet, cls.MangaDex]


class SauceNao(object):
    """"
    small script to work with SauceNao locally
    """

    SEARCH_POST_URL = 'http://saucenao.com/search.php'

    # all available account types, unregistered (always if no API key is passed), basic or premium
    ACCOUNT_TYPE_UNREGISTERED = ""
    ACCOUNT_TYPE_BASIC = "basic"
    ACCOUNT_TYPE_PREMIUM = "premium"

    # individual search usage limitations
    LIMIT_30_SECONDS = {
        ACCOUNT_TYPE_UNREGISTERED: 4,
        ACCOUNT_TYPE_BASIC: 6,
        ACCOUNT_TYPE_PREMIUM: 15,
    }

    # 0=html, 2=json but json is omitting important data but includes more data about authors
    # taken from the API documentation(requires login): https://saucenao.com/user.php?page=search-api
    API_HTML_TYPE = 0
    API_JSON_TYPE = 2

    CONTENT_CATEGORY_KEY = 'Material'
    CONTENT_AUTHOR_KEY = 'Creator'
    CONTENT_CHARACTERS_KEY = 'Characters'

    mime = None
    logger = None

    def __init__(self, directory, databases=SauceNaoDatabase.All, minimum_similarity=65, combine_api_types=False,
                 api_key=None, is_premium=False, exclude_categories='', move_to_categories=False,
                 use_author_as_category=False, output_type=API_HTML_TYPE, start_file=None, log_level=logging.ERROR,
                 title_minimum_similarity=90):
        """Initializing function

        :type directory: str
        :type databases: SauceNaoDatabase|int
        :type minimum_similarity: float
        :type combine_api_types: bool
        :type api_key: str
        :type is_premium: bool
        :type exclude_categories: str
        :type move_to_categories: bool
        :type use_author_as_category: bool
        :type output_type: int
        :type start_file: str
        :type log_level: int
        :type title_minimum_similarity: float
        """
        self.directory = directory
        self.databases = databases
        self.minimum_similarity = minimum_similarity
        self.combine_api_types = combine_api_types
        self.api_key = api_key
        self.is_premium = is_premium
        self.exclude_categories = exclude_categories
        self.move_to_categories = move_to_categories
        self.use_author_as_category = use_author_as_category
        self.output_type = output_type
        self.start_file = start_file
        self.title_minimum_similarity = title_minimum_similarity

        if self.api_key:
            if self.is_premium:
                account_type = self.ACCOUNT_TYPE_PREMIUM
            else:
                account_type = self.ACCOUNT_TYPE_BASIC
            self.search_limit_30s = self.LIMIT_30_SECONDS[account_type]
        else:
            self.search_limit_30s = self.LIMIT_30_SECONDS[self.ACCOUNT_TYPE_UNREGISTERED]

        if self.combine_api_types:
            # if we combine the API types we require twice as many API requests, so half the limit per 30 seconds
            self.search_limit_30s /= 2

        self.previous_status_code = None

        self.mime = MimeTypes()
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger("saucenao_logger")

        if SauceNaoDatabase.is_uncompleted(self.databases):
            self.logger.warning("Database #{db} is uncompleted and should not be used.".format(db=self.databases))

    def check_file(self, file_name: str) -> list:
        """Check the given file for results on SauceNAO

        :type file_name: str
        :return:
        """
        self.logger.info("checking file: {0:s}".format(file_name))
        if self.combine_api_types:
            result = self.__check_image(file_name, self.API_HTML_TYPE)
            sorted_results = self.parse_results_json(result)

            additional_result = self.__check_image(file_name, self.API_JSON_TYPE)
            additional_sorted_results = self.parse_results_json(additional_result)
            sorted_results = self.__merge_results(sorted_results, additional_sorted_results)
        else:
            result = self.__check_image(file_name, self.output_type)
            sorted_results = self.parse_results_json(result)

        filtered_results = self.__filter_results(sorted_results)
        return filtered_results

    def __get_http_data(self, file_path: str, output_type: int):
        """Prepare the http relevant data(files, headers, params) for the given file path and output type

        :param file_path:
        :param output_type:
        :return:
        """
        with open(file_path, 'rb') as file_object:
            files = {'file': file_object.read()}

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

        return files, params, headers

    def __check_image(self, file_name: str, output_type: int) -> str:
        """Check the possible sources for the given file

        :type output_type: int
        :type file_name: str
        :return:
        """
        file_path = os.path.join(self.directory, file_name)

        files, params, headers = self.__get_http_data(file_path=file_path, output_type=output_type)
        link = requests.post(url=self.SEARCH_POST_URL, files=files, params=params, headers=headers)

        code, msg = http.verify_status_code(link, file_name)

        if code == http.STATUS_CODE_SKIP:
            self.logger.error(msg)
            return json.dumps({'results': []})
        elif code == http.STATUS_CODE_REPEAT:
            if not self.previous_status_code:
                self.previous_status_code = code
                self.logger.info(
                    "Received an unexpected status code (message: {msg}), repeating after 10 seconds...".format(msg=msg)
                )
                time.sleep(10)
                return self.__check_image(file_name, output_type)
            else:
                raise UnknownStatusCodeException(msg)
        else:
            self.previous_status_code = None

        if output_type == self.API_HTML_TYPE:
            return self.parse_results_html_to_json(link.text)

        return link.text

    @staticmethod
    def parse_results_html_to_json(html: str) -> str:
        """Parse the results and sort them descending by similarity

        :type html: str
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
    def parse_results_json(text: str) -> list:
        """Parse the results and sort them descending by similarity

        :type text: str
        :return:
        """
        result = json.loads(text)
        results = [res for res in result['results']]
        return sorted(results, key=lambda k: float(k['header']['similarity']), reverse=True)

    def __filter_results(self, sorted_results) -> list:
        """Return results with a similarity bigger or the same as the defined similarity from the arguments (default 65%)

        :type sorted_results: list|tuple|Generator
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
    def get_content_value(results, key: str):
        """Return the first match of Material in content
        multiple sites have a categorisation which SauceNao utilizes to provide it in the content section

        :type results: list|tuple|Generator
        :type key: str
        :return:
        """
        for result in results:
            if 'content' in list(result['data'].keys()):
                for content in result['data']['content']:
                    if re.search(r'{0:s}: .*'.format(key), content):
                        return ''.join(re.split(r'{0:s}: '.format(key), content)[1:]).rstrip("\n").split('\n')
        return ''

    @staticmethod
    def get_title_value(results, key: str):
        """Return the first match of Material in the title section
        SauceNAO provides the authors name in the title section f.e. if provided by the indexed entry

        :type results: list|tuple|Generator
        :type key: str
        :return:
        """
        for result in results:
            if 'title' in list(result['data'].keys()):
                if re.match('{0:s}: .*'.format(key), result['data']['title']):
                    return ''.join(re.split(r'{0:s}: '.format(key), result['data']['title'])[1:]).rstrip("\n") \
                        .split('\n')
        return ''

    @staticmethod
    def merge_dicts(x: dict, y: dict) -> dict:
        """Take x dictionary and insert/overwrite y dictionary values

        :type x: dict
        :type y: dict
        :return:
        """
        z = x.copy()
        z.update(y)
        return z

    def __merge_results(self, result: list, additional_result: list) -> list:
        """Merge two result arrays

        :type result: list
        :type additional_result: list
        :return:
        """
        if len(result) <= len(additional_result):
            length = len(result)
        else:
            length = len(additional_result)

        for i in range(length):
            for key in list(result[i].keys()):
                result[i][key] = self.merge_dicts(result[i][key], additional_result[i][key])

        return result
