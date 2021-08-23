import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
# import pyautogui
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import selenium


def main():
    load_dotenv()   # Load .env file
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 100)

    # Log in to Leetcode
    site_login(driver, wait)
    

    url = 'https://leetcode.com/problems/arranging-coins/'
    driver.get(url)
    breakpoint()
    
    """
    var element = document.querySelector(".editor-wrapper__1ru6");
    if (element)
        element.parentNode.removeChild(element);
    """

def site_login(webdr: WebDriver, wait: WebDriverWait):
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
        except TimeoutException:
            print("Timed out waiting for page to load")


if __name__ == "__main__":
    # execute only if run as a script
    main()