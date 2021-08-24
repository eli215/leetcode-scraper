import os
from dotenv import load_dotenv

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from pathlib import Path
import json

# import pyautogui
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import selenium


def save_cookies(driver: WebDriver, cookie_filename: str):
    cookies = driver.get_cookies()
    with open(cookie_filename, 'w', newline='') as cookie_file:
        json.dump(cookies, cookie_file)

def load_cookies(driver: WebDriver, cookie_filename: str):
    driver.get("https://leetcode.com")
    with open(cookie_filename, 'r', newline='') as cookie_file:
        cookies = json.load(cookie_file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()

def main():
    load_dotenv()   # Load .env file
    dirname = os.path.dirname(__file__)
    chromedata_dir = os.path.join(dirname, 'ChromeData')

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={chromedata_dir}")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=60)
    
    if not is_logged_in():
        log_in() 
    # Log in to Leetcode
       # cookies_filename = 'cookies.json'
    # site_login(driver, wait)

    # save_cookies(driver, cookies_filename)
    # driver.close()

    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(options=options)

    # load_cookies(driver, cookies_filename)
    # site_login(driver, wait)
    # driver.get("https://leetcode.com/")
    # with open('cookies.json', 'r', newline='') as cookie_file:
    #     cookies = json.load(cookie_file)
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)
    #     driver.refresh()
    # load_cookie(driver, 'cookies.json')

    

    # url = 'https://leetcode.com/problems/arranging-coins/'
    # driver.get(url)
    breakpoint()
    
    print("end ")
    """
    var element = document.querySelector(".editor-wrapper__1ru6");
    if (element)
        element.parentNode.removeChild(element);
    """

def is_logged_in(driver: WebDriver):
    pass

def log_in(webdr: WebDriver, wait: WebDriverWait):
    login_url = "https://leetcode.com/accounts/login/"
    usr = os.getenv('LEETCODE_USR')
    pwd = os.getenv('LEETCODE_PWD')

    if usr and pwd:
        webdr.get(login_url)

        try:
            loading_is_finished = EC.invisibility_of_element((By.CLASS_NAME, "spinner"))
            wait.until(loading_is_finished)

            webdr.find_element_by_name("login").send_keys(usr)
            webdr.find_element_by_name("password").send_keys(pwd)
            webdr.find_element_by_id("signin_btn").click()
            # save_cookie(webdr, 'cookies.json')
        except TimeoutException:
            print("Timed out waiting for page to load")

def load_cookie(driver, path):
    driver.delete_all_cookies()
    with open(path, 'r') as cookiesfile:
        cookies = json.load(cookiesfile)
        driver.get("https://leetcode.com")
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()


if __name__ == "__main__":
    # execute only if run as a script
    main()