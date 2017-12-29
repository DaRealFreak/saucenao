#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
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

from filehandler import FileHandler


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

    def __init__(self, directory):
        """
        initializing function

        :type directory: str
        :param directory:
        """
        self.directory = directory
        self.mime = MimeTypes()

        files = FileHandler.get_files(directory)

        if args.exclude_categories:
            excludes = [l.lower() for l in args.exclude_categories.split(",")]
        else:
            excludes = []

        for file_name in files:
            start_time = time.time()
            result = self.check_image(file_name, self.API_HTML_TYPE)
            sorted_results = self.parse_results_json(result, file_name)

            if args.combine_api_types:
                additional_result = self.check_image(file_name, self.API_JSON_TYPE)
                additional_sorted_results = self.parse_results_json(additional_result, file_name)
                sorted_results = self.merge_results(sorted_results, additional_sorted_results)

            filtered_results = self.filter_results(sorted_results)

            if args.move_to_categories:
                category = self.get_content_value(filtered_results, self.CONTENT_CATEGORY_KEY)
                if not category:
                    logger.info(u"no category found for file: {0:s}".format(file_name))
                    continue

                # sub categories we don't want to move like original etc
                if category.lower() in excludes:
                    logger.info(u"skipping excluded category: {0:s} ({1:s})".format(category, file_name))
                    continue

                logger.info(u"moving {0:s} to category: {1:s}".format(file_name, category))
                FileHandler.move_to_category(file_name, category, base_directory=args.dir)
            else:
                # ToDo: what exactly is the default case I want here?
                # possibly printing the list
                pass

            duration = time.time() - start_time
            if duration < (30 / self.LIMIT_30_SECONDS):
                logger.debug("sleeping '{:.2f}' seconds".format((30 / self.LIMIT_30_SECONDS) - duration))
                time.sleep((30 / self.LIMIT_30_SECONDS) - duration)

    @staticmethod
    def get_content_value(results, key):
        """
        return the first match of Material in content
        multiple sites have a categorisation which saucenao utilizes to provide it in the content section

        :type results: list
        :type key: str
        :param results:
        :param key:
        :return:
        """
        for result in results:
            if 'content' in result['data'].keys():
                for content in result['data']['content']:
                    if re.match('{0:s}: .*'.format(key), content):
                        return ''.join(re.split(r'{0:s}: '.format(key), content)[1:])
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
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
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

        for i in xrange(length):
            for key in result[i].keys():
                result[i][key] = self.merge_two_dicts(result[i][key], additional_result[i][key])

        return result

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
            'db': args.databases,
        }

        if args.api_key:
            params['api_key'] = args.api_key

        link = requests.post(url=self.SEARCH_POST_URL, files=files, params=params, headers=headers)

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
            # optional field in saucenao
            title_tag = res.find_next('div', attrs={"class": "resulttitle"})
            if title_tag:
                title = title_tag.text
            else:
                title = ''

            # mandatory field in saucenao
            similarity = res.find_next('div', attrs={"class": "resultsimilarityinfo"}).text.replace('%', '')
            alternate_links = [a_tag['href'] for a_tag in
                               res.find_next('div', attrs={"class": "resultmiscinfo"}).find_all('a', href=True)]
            content_column = []
            content_column_tags = res.find_all('div', attrs={"class": "resultcontentcolumn"})
            for content_column_tag in content_column_tags:
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
    def parse_results_json(text, file_name):
        """
        parse the results and sort them descending by similarity

        :type text: str
        :type file_name: str
        :param text:
        :param file_name:
        :return:
        """
        result = json.loads(text)

        if not result['results']:
            logger.info('No results found for image: {0:s}'.format(file_name))

        results = [res for res in result['results']]
        return sorted(results, key=lambda k: float(k['header']['similarity']), reverse=True)

    @staticmethod
    def filter_results(sorted_results):
        """
        return results with a similarity bigger or the same as the defined similarity from the arguments (default 65%)

        :type sorted_results: list
        :param sorted_results:
        :return:
        """
        filtered_results = []
        for res in sorted_results:
            if float(res['header']['similarity']) >= float(args.minimum_similarity):
                filtered_results.append(res)
            else:
                # we can break here since the results are sorted by similarity anyways
                break
        return filtered_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='directory to sort', required=True)
    parser.add_argument('-db', '--databases', default=999, type=int, help='which databases should be searched')
    parser.add_argument('-min', '--minimum_similarity', default=65, type=float, help='minimum similarity percentage')
    parser.add_argument('-c', '--combine-api-types', action='store_true', help='combine html and json api response to '
                                                                               'retrieve more information')
    parser.add_argument('-k', '--api-key', help='API key of your account on saucenao')
    parser.add_argument('-x', '--exclude-categories', type=str, help='exclude specific categories from moving')
    parser.add_argument('-mv', '--move-to-categories', action='store_true', help='move images to categories')
    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    SauceNao(args.dir)
