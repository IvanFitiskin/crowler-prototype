from insta_account import InstaAccount
from insta_post import InstaPost
from html_tags_reader import HTMLTags
from post_parser import PostParser
from utils import insta_login

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions

from bs4 import BeautifulSoup
import hashlib

import copy
import csv
import logging
import os
import random
import re
import sys
import time

class InstaShuttle:
    insta_logger = logging.getLogger('instagram_parser')

    ACCOUNTS_DATA_FILE_HEADER = [ 'id'
                                , 'insta_name'
                                , 'name'
                                , 'description'
                                , 'links'
                                , 'followers'
                                , 'followers'
    ]

    POSTS_DATA_FILE_HEADER    = [ 'post_id'
                                , 'user_id'
                                , 'url'
                                , 'date'
                                , 'photo'
                                , 'photo_file'
                                , 'likes'
                                , 'marked_users'
                                , 'marked'
                                , 'hash_tags'
                                , 'description'
    ]

    POSTS_BY_TAG_DATA_FILE_HEADER = [ 'post_id'
                                    , 'author'
                                    , 'tag'
                                    , 'url'
                                    , 'date'
                                    , 'photo'
                                    , 'photo_file'
                                    , 'likes'
                                    , 'marked_users'
                                    , 'marked'
                                    , 'hash_tags'
                                    , 'description'
    ]

    TAG_RE = re.compile(r'<[^>]+>|[/]*react-text[:\s0-9]*')
    REMOVE_SYMBOLS = re.compile(r'[;\n]+')

    def __init__(self, webdriver, tags, data_folder=None):
        self.webdriver    = webdriver
        self.tags         = tags
        self.data_folder  = data_folder
        self.data_file    = os.path.join(self.data_folder, 'account_data.csv')
        self.post_file    = os.path.join(self.data_folder, 'raw_posts.csv')
        self.image_folder = os.path.join(self.data_folder, 'images')
        self.post_parser  = PostParser(self.tags)
        self.parsed_post  = []


    def __clean_webdriver(self):
        num_of_tabs = len(self.webdriver.window_handles)
        for x in range(1, num_of_tabs):
            self.webdriver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'W')


    def __load_up_posts(self, count):
        self.insta_logger.info('loading up posts list')
        try:
            more_button = None
            for element in self.webdriver.find_elements_by_tag_name('a'):
                if element.text == 'Load more' or element.text == 'Загрузить еще':
                    more_button = element
                    break
            more_button.click()
        except Exception as inst:
            self.insta_logger.error("cannot click button: {0}".format(inst))
        else:
            self.insta_logger.info("posts list sucessfully loaded up")
        # scrolls a window in down
        for i in range(max(count, 10)):
            self.webdriver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            self.webdriver.execute_script('window.scrollTo(0, 0)')
        self.webdriver.execute_script('window.scrollTo(0, 0)')


    def __load_up_followers(self, count):
        self.insta_logger.info('loading up followers list')
        try:
            followers_button = None
            for element in self.webdriver.find_elements_by_tag_name('a'):
                if 'follower' in element.get_attribute('href'):
                    followers_button = element
                    break

            followers_button.click()
            followers_count = followers_button.find_elements_by_tag_name('span')[0]
            if followers_count.get_attribute('title') == '':
                followers_count = int(followers_count.text.replace(",", ""))
            else:
                followers_count = int(followers_count.get_attribute('title').replace(",", ""))
            self.insta_logger.info('followers count: {0}'.format(followers_count))

            followers_div = None
            for element in self.webdriver.find_elements_by_tag_name('div'):
                if 'Followers' in element.text:
                    followers_div = element
                    break
            # TO DO: made right loading full followers list
            for index in range(min(count, followers_count)):
                self.webdriver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',followers_div)
        except Exception as inst:
            self.insta_logger.error("cannot find followers: {0}".format(inst))
        else:
            self.insta_logger.info('followers list sucessfully loaded up')


    def __get_account_info(self, soup):
        # get surface info about user
        user_info = soup.find_all('div', attrs={'class' : self.tags.info_class})[0]
        user_soup = BeautifulSoup(str(user_info.contents), 'html.parser')
        user_name = user_soup.find_all('h2', attrs={'class' : self.tags.name_class})

        if len(user_name) > 0:
            user_name = user_name[0].contents[0]
        else:
            user_name = insta_name
        user_links = user_soup.find_all('a', attrs={'class' : self.tags.link_class})
        user_links = [link.contents[0] for link in user_links]
        user_descr = ' '.join([self.TAG_RE.sub('', str(span.contents)) for span in user_soup.find_all('span')])
        user_descr = self.REMOVE_SYMBOLS.sub(' ', user_descr)
        return user_name, user_descr, user_links


    def __get_account_posts(self, soup, count, insta_name, russian_only, from_search=False):
        parsed_posts = []
        posts = soup.find_all('a' if from_search else 'div')
        posts_count = len(posts) if count == -1 else min([count+1, len(posts)])
        post_index = 0
        self.insta_logger.info('start fetching {0} posts data'.format(count))

        self.post_parser = PostParser(self.tags)
        failed_posts = 0
        for index, link in enumerate(posts):
            try:
                link_class = ' '.join(link['class'])
                if post_index < posts_count and link_class == self.tags.post_class:
                    try:
                        if not from_search:
                            link = link.find_all('a')[0]
                        self.insta_logger.info('****** post {0} from {1} (possibly)'.format(post_index, len(posts)))
                        post, author = self.post_parser.parse_post( link['href']
                                                                  , insta_name
                                                                  , self.image_folder
                                                                  , russian_only)
                        if post:
                            if not from_search:
                                yield post
                            else:
                                yield author, post
                            post_index+=1
                            if post_index % 20:
                                self.post_parser.clear_cash()
                        else:
                            failed_posts += 1
                    except Exception as detailed:
                        self.insta_logger.error('cannot parse post: {0}'.format(detailed))
                        failed_posts += 1
                        continue
            except KeyError:
                continue
            if failed_posts >= 10:
                break
        self.post_parser.clear_cash()


    def __get_account_followers(self, soup, followers):
        user_followers = []
        links = soup.find_all('a')
        for index, link in enumerate(links):
            try:
                link_class = ' '.join(link['class'])
                if link_class == self.tags.followers_class:
                    user_followers.append(link.contents[0])
            except Exception:
                continue

        random.shuffle(user_followers)
        random_followers = []
        if len(user_followers) > 0:
            random_followers = user_followers[0:min(len(user_followers), followers)]
        return user_followers, random_followers


    # warning: we do not output comments
    def __save_account_data( self
                           , acc
                           , comments
                           , data_writer
                           , post_writer):
        # print account data
        account_index = acc.index()
        data_writer.writerow([ account_index
                             , acc.insta_name
                             , acc.name
                             , acc.description[0]
                             , ','.join(acc.description[1])
                             , ','.join(acc.followers)
                             , ','.join(acc.followers)
        ])
        # print posts data
        for post in acc.posts:
            post_writer.writerow([ post.index(acc.insta_name)
                                 , account_index
                                 , post.url
                                 , post.date
                                 , post.photo
                                 , post.photo_file
                                 , post.likes
                                 , ','.join(post.marks)
                                 , ','.join(post.descr[1])
                                 , ','.join(post.descr[2])
                                 , post.descr[0]
        ])


    def _fetch_accounts_data( self
                            , insta_names
                            , data_writer
                            , post_writer
                            , count=20
                            , comments=False
                            , images=False
                            , followers=0
                            , use_hashtags=False
                            , depth_level=5
                            , account_list=set()
                            , russian_only=False):
        depth_level_list = [depth_level] * len(insta_names)
        account_index = 0

        while len(insta_names) != 0:
            self.insta_logger.info('**************************************************')
            self.insta_logger.info('count of fetching accounts: {0}'.format(len(insta_names)))
            insta_name          = insta_names.pop()
            already_fetched = insta_name in account_list
            current_depth_level = depth_level_list.pop()

            self.insta_logger.info('fetching {0} data | depth: {1}, already_fetched: {2}'
                                   .format(insta_name, current_depth_level, already_fetched))
            try:
                # fetch data from account
                account_data, user_followers = self.get_account_data( insta_name
                                                                    , count
                                                                    , comments
                                                                    , images
                                                                    , followers
                                                                    , use_hashtags
                                                                    , russian_only
                                                                    , already_fetched
                                                                    )
                if not already_fetched:
                    self.__save_account_data( account_data
                                            , comments
                                            , data_writer
                                            , post_writer
                                            )

                if current_depth_level > 1:
                    for follower in user_followers:
                        insta_names.append(follower)
                        depth_level_list.append(current_depth_level - 1)

                account_list.add(insta_name)
                account_index += 1
                if account_index % 20 == 1:
                    self.__clean_webdriver()

            except Exception as detailed:
                self.insta_logger.error('cannot fetch data: {0}'.format(detailed))
                continue

    def fetch_accounts_data( self
                           , insta_names
                           , count=20
                           , comments=False
                           , images=False
                           , followers=0
                           , use_hashtags=False
                           , depth_level=5
                           , russian_only=False):
        data_file_exists = os.path.isfile(self.data_file)
        post_file_exists = os.path.isfile(self.post_file)
        # read already fetched accounts
        # in this version we think that if account exists
        # we shouldn't fetch data from it (except users list)
        account_list = set()
        if data_file_exists:
            for row in csv.reader(open(self.data_file, 'r'), delimiter =';'):
                account_list.add(row[1])
        # start fetching data from accounts
        with open(self.data_file, "a" if data_file_exists else "w") as datafile:
            data_writer = csv.writer(datafile, delimiter =';',quoting=csv.QUOTE_MINIMAL)
            if not data_file_exists:
                data_writer.writerow(self.ACCOUNTS_DATA_FILE_HEADER)
            with open(self.post_file, "a" if post_file_exists else "w") as postfile:
                post_writer = csv.writer(postfile, delimiter =';',quoting=csv.QUOTE_MINIMAL)
                if not post_file_exists:
                    post_writer.writerow(self.POSTS_DATA_FILE_HEADER)
                self.insta_logger.info('start fetching instgram data from {0} primary accounts'.
                                       format(len(insta_names)))
                self._fetch_accounts_data( insta_names
                                         , data_writer
                                         , post_writer
                                         , count
                                         , comments
                                         , images
                                         , followers
                                         , use_hashtags
                                         , depth_level
                                         , account_list
                                         , russian_only
                                         )


    def get_account_data( self
                        , insta_name
                        , count
                        , comments
                        , images
                        , followers
                        , use_hashtags
                        , russian_only
                        , fetched_already):
        self.insta_logger.info("get account {0} page".format(insta_name))
        # pass the address of the page
        self.webdriver.get("https://www.instagram.com/{0}/".format(insta_name))
        self.insta_logger.info("page loaded")
        self.__load_up_posts(count)
        self.__load_up_followers(followers)

        # save in 'soup' whole page code
        soup = BeautifulSoup(self.webdriver.page_source, 'html.parser')

        # get user's infromation
        user_name, user_descr, user_links = self.__get_account_info(soup)
        posts = []
        if not fetched_already:
            posts = [p for p in self.__get_account_posts(soup, count, insta_name, russian_only)]
        user_followers, random_followers = self.__get_account_followers(soup, followers)
        self.insta_logger.info('fecth more data from {0} random followers: {1}'.format(followers, ' '.join(random_followers)))
        return InstaAccount(insta_name, user_name, (user_descr, user_links), posts, [], user_followers), random_followers


    def _fetch_search_posts_by_tag( self
                                  , tag
                                  , count
                                  , used_posts=set()
                                  , comments=False
                                  , images=True
                                  , use_hash_tags=True):
        self.insta_logger.info("get tag {0} search page".format(tag))
        #We pass the address of the page
        self.webdriver.get("https://www.instagram.com/explore/tags/{0}/".format(tag))
        self.insta_logger.info("page loaded")
        self.__load_up_post()

        # save in 'soup' whole page code
        soup = BeautifulSoup(self.webdriver.page_source, 'html.parser')
        # resend generator
        posts = self.__get_account_posts(soup, count, None, russian_only, True)
        return posts


    def fetch_search_posts( self
                          , tags_list
                          , posts_count=100
                          , comments=False
                          , images=True
                          , use_hash_tags=True):
        self.insta_logger.info('start fetching data from search | count of tags: {0}'.format(len(tags_list)))
        post_file = '{0}_search_only'.format(self.post_file)
        post_file_exists = os.path.isfile(post_file)
        with open(post_file, "a" if post_file_exists else "w") as postfile:
            post_writer = csv.writer(postfile, delimiter =';',quoting=csv.QUOTE_MINIMAL)
            if not post_file_exists:
                post_writer.writerow(POSTS_BY_TAG_DATA_FILE_HEADER)
            for tag_index, tag in enumerate(tags_list):
                for author, post in _fetch_search_posts_by_tag(tag, posts_count, used_posts, comments, images, use_hash_tags):
                    post_writer.writerow([ post.index(author)
                                         , author
                                         , tag
                                         , post.url
                                         , post.date
                                         , post.photo
                                         , post.photo_file
                                         , post.likes
                                         , ','.join(post.marks)
                                         , ','.join(post.descr[1])
                                         , ','.join(post.descr[2])
                                         , post.descr[0]])
