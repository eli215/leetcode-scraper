import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pyautogui


# Note: research logging best practices
LOGFILE = "leetcode_scraper_log.txt"


def main():
    # Initial setup
    load_dotenv()   # Load .env file
    dirname = os.path.dirname(__file__)
    chromedata_dir = os.path.join(dirname, 'ChromeData')

    # Initialize webdriver
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={chromedata_dir}")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=60)
    
    # Log in to Leetcode
    if not is_logged_in():
        log_in(driver, wait) 
    
    # Navigate to problem URL, check validity (?)
    # - flag whether it has a Solution page?
    # url = 'https://leetcode.com/problems/arranging-coins/'
    # driver.get(url)

    # Modify Description page HTML w/ JS
    # - remove code window on right
    """
    var element = document.querySelector(".editor-wrapper__1ru6");
    if (element)
        element.parentNode.removeChild(element);
    """
    # - set left flexbox fill to '1' to fill page width
    # - if Solution exists, set its menu item href to our local copy


    # Save Description page w/ right click Save As

    # Navigate to Solution URL (if applicable)

    # Modify page HTML w/ JS
    # - same stuff as above
    # - set Description menu item href to our local copy


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


if __name__ == "__main__":
    # execute only if run as a script
    main()