#!/bin/env python2.7
# -*- coding: utf-8 -*-

from apollo_initializer import get_shuttle

import argparse
import copy
import datetime
import getpass
import logging
import os
import re

logging.basicConfig( format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
                   , level=logging.INFO)
main_logger = logging.getLogger('main')

def parse_args():
    DEFAULT_OUTDIR       = '.'
    DEFAULT_USER         = 'vanyaninja'
    DEFAULT_PASSWORD     = None
    DEFAULT_USERS        = 'kefir.p'
    DEFAULT_DRIVER       = '/home/ivan/Utilities/webdrivers/geckodriver'
    DEFAULT_HTML_TAGS    = 'tags.ini'
    DEFAULT_POSTS_COUNT  = 100
    DEFAULT_FOLLOWINGS   = 5
    DEFAULT_COMMENTS     = False
    DEFAULT_IMAGES       = False
    DEFAULT_HASHTAGS     = False
    DEFAULT_DEPTH        = 3
    DEFAULT_RUSSIAN_ONLY = False
    parser = argparse.ArgumentParser(description='fetch instagram accounts data')
    parser.add_argument('-u'
                       , '--user'
                       , type=str
                       , default=DEFAULT_USER
                       , help="user login (default: {0})".format(DEFAULT_USER)
                       )
    parser.add_argument('-p'
                       , '--password'
                       , type=str
                       , default=DEFAULT_PASSWORD
                       , help="user password (default: {0})".format(DEFAULT_PASSWORD)
                       )
    parser.add_argument('-o'
                       , '--outdir'
                       , type=str
                       , default=DEFAULT_OUTDIR
                       , help="output directory (default: {0})".format(DEFAULT_OUTDIR)
                       )
    parser.add_argument('-l'
                       , '--users-list'
                       , type=str
                       , default=DEFAULT_USERS
                       , help="fetch users list or file with list (default: {0})".format(DEFAULT_USERS)
                       )
    parser.add_argument('-c'
                       , '--posts-count'
                       , type=int
                       , default=DEFAULT_POSTS_COUNT
                       , help="used posts count (default: {0})".format(DEFAULT_POSTS_COUNT)
                       )
    parser.add_argument('-f'
                       , '--followings'
                       , type=int
                       , default=DEFAULT_FOLLOWINGS
                       , help="fetch each n random following too (default: {0})".format(DEFAULT_FOLLOWINGS)
                       )
    parser.add_argument('-d'
                       , '--driver'
                       , type=str
                       , default=DEFAULT_DRIVER
                       , help="path to firefox geckodriver (default: {0})".format(DEFAULT_DRIVER)
                       )
    parser.add_argument('-t'
                       , '--html-tags-file'
                       , type=str
                       , default=DEFAULT_HTML_TAGS
                       , help="file with used html tags map (default: {0})".format(DEFAULT_HTML_TAGS)
                       )
    parser.add_argument('--comments'
                       , action='store_true'
                       , default=DEFAULT_COMMENTS
                       , help="get users comments too (default: {0})".format(DEFAULT_COMMENTS)
                       )
    parser.add_argument('--images'
                       , action='store_true'
                       , default=DEFAULT_IMAGES
                       , help="get posts photo too (default: {0})".format(DEFAULT_IMAGES)
                       )
    parser.add_argument('--use-hashtags'
                       , action='store_true'
                       , default=DEFAULT_HASHTAGS
                       , help="get posts only with hashtags (default: {0})".format(DEFAULT_HASHTAGS)
                       )
    parser.add_argument('--depth-level'
                       , type=int
                       , default=DEFAULT_DEPTH
                       , help="default depth (default: {0})".format(DEFAULT_DEPTH)
                       )
    parser.add_argument('--russian-only'
                       , action='store_true'
                       , default=DEFAULT_RUSSIAN_ONLY
                       , help="get posts only containing russian letters (default: {0})".format(DEFAULT_RUSSIAN_ONLY)
                       )
    settings = parser.parse_args()
    if os.path.isfile(settings.users_list):
        settings.users_list = [u.strip() for u in open(settings.users_list, 'r')]
    else:
        settings.users_list = [u.strip() for u in settings.users_list.split(',')]
    return settings


def start_fetching(settings):
    main_logger.info('START FETCHING ACCOUNTS DATA')
    try:
        shuttle = get_shuttle(settings.driver, settings.user, settings.password, settings.outdir, settings.html_tags_file)
        shuttle.fetch_accounts_data( settings.users_list
                                   , settings.posts_count
                                   , settings.comments
                                   , settings.images
                                   , settings.followings
                                   , settings.use_hashtags
                                   , settings.depth_level
                                   , settings.russian_only
                                   )
    except Exception as detailed:
        main_logger.error('FETCHING DATA FAILED: {0}'.format(detailed))
    else:
        main_logger.info('FETCHING DATA FINISHED SUCCESSFULLY')


def main():
    settings = parse_args()
    start_fetching(settings)


if __name__ == '__main__':
    main()
