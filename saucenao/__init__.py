#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import logging

from .filehandler import FileHandler
from .saucenao import SauceNao


def run_application():
    """
    run SauceNao based on arguments passed to the file

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='directory to sort', required=True)
    parser.add_argument('-db', '--databases', default=999, type=int, help='which databases should be searched')
    parser.add_argument('-min', '--minimum_similarity', default=65, type=float,
                        help='minimum similarity percentage')
    parser.add_argument('-c', '--combine-api-types', action='store_true',
                        help='combine html and json api response to '
                             'retrieve more information')
    parser.add_argument('-k', '--api-key', help='API key of your account on SauceNao')
    parser.add_argument('-x', '--exclude-categories', type=str, help='exclude specific categories from moving')
    parser.add_argument('-mv', '--move-to-categories', action='store_true', help='move images to categories')
    parser.add_argument('-o', '--output-type', default=0, type=int, help='0(html) or 2(json) API response')
    parser.add_argument('-sf', '--start-file', help='with which file the checks start in case of after reaching the '
                                                    'daily limit')
    parser.add_argument('-log', '--log-level', default=logging.ERROR, type=int, help='which log level should be used, '
                                                                                     'check logging._levelNames for '
                                                                                     'options')
    args = parser.parse_args()

    files = FileHandler.get_files(args.dir)
    sauce_nao = SauceNao(args.dir, databases=args.databases, minimum_similarity=args.minimum_similarity,
                         combine_api_types=args.combine_api_types, api_key=args.api_key,
                         exclude_categories=args.exclude_categories, move_to_categories=args.move_to_categories,
                         start_file=args.start_file, log_level=args.log_level)
    return sauce_nao.check_files(files)
