from apollo_alliance import InstaShuttle
from html_tags_reader import HTMLTags
from utils import insta_login

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging

def get_shuttle(gecko_driver_path, user_name, password=None, data_folder=None, init_file='tags.ini'):
    init_logger = logging.getLogger('apollo_initializer')
    dcap = dict(DesiredCapabilities.FIREFOX)
    dcap['marionette'] = True
    init_logger.info('loading gecko driver: {0}'.format(gecko_driver_path))
    driver = webdriver.Firefox(capabilities=dcap,executable_path=gecko_driver_path)
    init_logger.info('dirver loaded')

    init_logger.info('login in instagram with {0} account'.format(user_name))
    insta_login(driver, user_name, password)

    init_logger.info('login finished successfully')

    html_tags = HTMLTags(init_file)
    shuttle = InstaShuttle(driver, html_tags, data_folder)

    return shuttle
