from insta_post import InstaPost
from html_tags_reader import HTMLTags

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import logging
import math
import re
import sys
import time
import wget


class PostParser:
    parser_logger = logging.getLogger('instagram_post_parser')

    __RUSSIAN_CHECKER  = re.compile('[А-ЯЁа-яё]+')
    __TAG_RE      = re.compile(r'<[^>]+>|[/]*react-text[:\s0-9]*')
    __MARKS_RE    = re.compile(r'@[a-zA-Z\._0-9]+')
    __HASHTAGS_RE = re.compile(r'#[a-zA-Z\._0-9]+')

    def __init__(self, tags):
        dcap = dict(DesiredCapabilities.CHROME)
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.tags = tags


    def clear_cash(self):
        try:
            num_of_tabs = len(self.driver.window_handles)
            for x in range(1, num_of_tabs):
                self.driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'W')
        except Exception as e:
            print(e)
            self.driver.quit()
            self.__init__()


    def __get_post_author(self, soup):
        account = ''
        links = soup.find_all('a')
        for link in links:
            link_class = ' '.join(link['class'])
            if link_class == self.tags.usr_name_a_class:
                account = link['href'].replace('/', '')
                break
        return account


    def __get_post_image(self, soup, photos_folder):
        image = soup.find_all('img')
        if len(image) == 0:
            image = ''
        elif len(image) == 1:
            image = image[0]['src']
        else:
            image = image[1]['src']
        photo_file = None
        # download photos from the post
        if photos_folder:
           photo_file = wget.download(image, photos_folder, bar=None)
        return image, photo_file


    def __get_likes_count(self, soup):
        likes = soup.find_all('span', attrs={'class' : self.tags.likes_span_class})
        likes_count = 0
        # output number of likes
        if len(likes) > 0:
            likes_label = likes[0].find_all('span')[0].contents[0].replace(',', '')
            if (likes_label[-1] in ('k', 'm')):
                base = 10 ** (3 if likes_label[-1] == 'k' else 6)
                mul = float(str(likes_label[:len(likes_label) - 1]).replace(',', '.', 1))
                likes_count = int(base * mul)
            elif (likes_label[len(likes_label) - 3 : len(likes_label)] == 'млн'):
                base = 10 ** 6
                mul = float(str(likes_label[:len(likes_label) - 3]).replace(',', '.', 1))
                likes_count = int(base * mul)
            elif (likes_label[len(likes_label) - 4 : len(likes_label)] == 'тыс.'):
                base = 10 ** 3
                mul = float(str(likes_label[:len(likes_label) - 4]).replace(',', '.', 1))
                likes_count = int(base * mul)
            else:
                likes_count = int(likes_label)
        return likes_count


    def __get_post_timestamp(self, soup):
        return soup.find_all('time', attrs={'class' : self.tags.date_time_class})[0]['title']


    def __find_description(self, comments, author):
        descr = ('',[],[])
        if len(comments) > 0:
            for comment in comments:
                if comment[0] == author:
                    descr = comment[1]
                    break
        return descr


    def __parse_description(self, description):
        # parse description in part
        if not type(description) is str:
            text = description.find_all('span')
            description_text = ''
            marked = []
            hash_tags = []
            if len(text) > 0:
                description_text = ' '.join([self.__TAG_RE.sub('', str(c)) for c in text[0].contents])
                # parsed special words from text
                marked           = [ mark[1:] for mark in self.__MARKS_RE.findall(description_text)]
                hash_tags        = [ tag[1:]  for tag  in self.__HASHTAGS_RE.findall(description_text)]
            return (description_text, marked, hash_tags)
        else:
            return ('',[],[])


    def __get_load_more_button(self):
        # search button "load more" to scroll through the comments
        buttons = self.driver.find_elements_by_tag_name('a')
        load_more = None
        for button in buttons:
            if button.get_attribute('class') == self.tags.more_comments:
                load_more = button
                break
        return load_more


    def __get_marked_accounts(self, soup):
        # search marked accounts
        mark_div = soup.find_all('div', attrs={'class' : self.tags.mark_class})
        if len(mark_div) > 0:
            mark_div = mark_div[0]
            marks = mark_div.find_all('a', attrs={'class' : self.tags.photo_a_class})
            marks = [self.__TAG_RE.sub('', str(mark.contents[0])) for mark in marks]
            return marks
        else:
            return []


    def __get_all_comments(self, soup):
        # search all comments
        found_buttons = soup.find_all('a', attrs={'class' : self.tags.more_comments})
        # TO DO: greping additional comments count
        count_of_additional_comments = 100
        # click on the button "load more" several times
        for index in range(count_of_additional_comments // 20):
            load_more = self.__get_load_more_button()
            if load_more:
                load_more.click()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        comments = list(filter(lambda comment: ' '.join(comment['class']) == self.tags.comment_li_class, soup.find_all('li')))
        full_comments = []
        # write a comment of the author and description
        for comment in comments:
            author_com = comment.find_all('a')[0].contents[0]
            descr_com = self.__parse_description(comment)
            full_comments.append((author_com, descr_com))
        return full_comments


    def parse_post(self, post, account, photos_folder=None, russian_only=False):
        # parsing post URL
        parse_post_link = post.split('/')
        post_url = 'https://www.instagram.com{0}'.format('/'.join(parse_post_link[:len(parse_post_link) - 1]))
        self.driver.get(post_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        comments          = self.__get_all_comments(soup)
        descr             = self.__find_description(comments, account)
        if russian_only:
            if len(PostParser.__RUSSIAN_CHECKER.findall(descr[0])) == 0:
                self.parser_logger.warning('post not used russian symbols - missing post')
                return None, None
        if not account:
            account = self.__get_post_author(soup)
        image, photo_file = self.__get_post_image(soup, photos_folder)
        likes_count       = self.__get_likes_count(soup)
        post_time         = self.__get_post_timestamp(soup)
        marks             = self.__get_marked_accounts(soup)
        self.parser_logger.info('********** account: {0}, URL: {1}, image: {2}, comments: {3}'.format(account, post,  'Yes' if image else 'No', len(comments)))
        posts = InstaPost(post_url, image, descr, likes_count, post_time, comments, marks, photos_folder, photo_file)
        return posts, account
