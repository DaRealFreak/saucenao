#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging

from saucenao.files import Constraint, FileHandler, Filter
from saucenao.saucenao import SauceNao, SauceNaoDatabase
from saucenao.worker import Worker

__all__ = [SauceNao, SauceNaoDatabase, FileHandler, Filter, Constraint]


def run_application():
    """Run SauceNao based on arguments passed to the file

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='directory to sort', required=True)
    parser.add_argument('-db', '--databases', default=999, type=int, help='which databases should be searched')
    parser.add_argument('-min', '--minimum-similarity', default=65, type=float,
                        help='minimum similarity percentage')
    parser.add_argument('-c', '--combine-api-types', action='store_true',
                        help='combine html and json api response to retrieve more information')
    parser.add_argument('-k', '--api-key', help='API key of your account on SauceNao')
    parser.add_argument('-p', '--premium', help='is API key related user premium')
    parser.add_argument('-x', '--exclude-categories', type=str, help='exclude specific categories from moving')
    parser.add_argument('-mv', '--move-to-categories', action='store_true', help='move images to categories')
    parser.add_argument('-author', '--use-author-as-category', default=False, action='store_true',
                        help='use author as category key instead of material')
    parser.add_argument('-o', '--output-type', default=0, type=int, help='0(html) or 2(json) API response')
    parser.add_argument('-sf', '--start-file',
                        help='with which file the checks start in case of after reaching the daily limit')
    parser.add_argument('-log', '--log-level', default=logging.ERROR, type=int,
                        help='which log level should be used, check logging._levelNames for options')

    parser.add_argument('-fcrdt', '--filter-creation-date', type=str,
                        help='filters files for created after given date. '
                             'Format of date has to match "d.m.Y[ H:M[:S]]"')
    parser.add_argument('-fmdt', '--filter-modified-date', type=str,
                        help='filters files for modified after given date. '
                             'Format of date has to match "d.m.Y[ H:M[:S]]"')

    parser.add_argument('-tmin', '--title-minimum-similarity', default=95, type=float,
                        help='minimum similarity percentage for title search with BakaUpdates, MyAnimeList and '
                             'VisualNovelDatabase')

    args = parser.parse_args()

    file_filter = Filter(assert_is_file=True)
    if args.filter_creation_date:
        file_filter._filter_creation_date = Constraint(value=args.filter_creation_date,
                                                       cmp_func=Constraint.cmp_value_bigger_or_equal)
    if args.filter_modified_date:
        file_filter._filter_modified_date = Constraint(value=args.filter_modified_date,
                                                       cmp_func=Constraint.cmp_value_bigger_or_equal)
    working_files = FileHandler.get_files(args.dir, file_filter)

    saucenao_worker = Worker(files=working_files, directory=args.dir, databases=args.databases,
                             minimum_similarity=args.minimum_similarity, combine_api_types=args.combine_api_types,
                             api_key=args.api_key, is_premium=args.premium,
                             exclude_categories=args.exclude_categories, move_to_categories=args.move_to_categories,
                             use_author_as_category=args.use_author_as_category, start_file=args.start_file,
                             log_level=args.log_level, title_minimum_similarity=args.title_minimum_similarity)
    return saucenao_worker.run()
