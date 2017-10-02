from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import copy
import getpass
import sys
import time
import os

# make your webdriver add available to use full instagram functionality
def insta_login(driver, user_name, password=None):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.LINK_TEXT, "Sign up")))
    try:
        name_input = None
        pass_input = None

        for element in driver.find_elements_by_tag_name('input'):
            if element.get_attribute('name') == 'username':
                name_input = element
            if element.get_attribute('name') == 'password':
                pass_input = element

        time.sleep(0.05)
        name_input.click()
        name_input.send_keys(user_name)
        pass_input.click()

        if not password:
            print('*** username: {0}'.format(user_name))
            password = getpass.getpass('*** password:')

        pass_input.send_keys(password)

        login_button = None
        for element in driver.find_elements_by_tag_name('button'):
            if element.text == 'Log in':
                login_button = element
        login_button.click()

        WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, "Activity Feed")))
    except Exception as inst:
        print("Cannot click button: {0}".format(str(inst)))
        driver.close()
        sys.exit(0)
