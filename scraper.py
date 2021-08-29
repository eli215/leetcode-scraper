import os
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pyautogui

# Note: research logging best practices
LOGFILE = "leetcode_scraper_log.txt"
HOME_URL = "https://leetcode.com"
LOGIN_URL = "https://leetcode.com/accounts/login"

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

    driver.get(HOME_URL)
    # Log in to Leetcode if necessary
    if not is_logged_in(driver, wait):
        log_in(driver, wait)
    
    # Collect all problem URLs from problemset pages
    # Add to a JSON file?
    """
    title:
    url:
    filename:
    solution {
        type:
        exists:
    }
    acceptance:
    difficulty:
    frequency:
    """
    # Loop through all problems (that aren't already downloaded?)

    # Navigate to problem URL, check validity (?)
    # - flag whether it has a Solution page?
    # url = 'https://leetcode.com/problems/arranging-coins/'
    # driver.get(url)

    # has_solution = driver.execute_script("""
    #     return document.querySelector('[data-key="solution"]').getAttribute("data-disabled") == true;
    # """)

    update_problemset(driver, wait)
    breakpoint()
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


def update_problemset(driver: WebDriver, wait: WebDriverWait):

    PROBLEMSET_URL = "https://leetcode.com/problemset/all/"
    driver.get(PROBLEMSET_URL)

    finished = False

    while not finished:

        table_html = driver.execute_script(
            """
                return document.querySelector('div[role="rowgroup"]').innerHTML;
            """
        )

        soup = BeautifulSoup(table_html, 'html.parser')
        # rows = soup.findAll("div", {"role" : "row"})
        for row in soup.find_all("div", {"role" : "row"}):
            # cells = BeautifulSoup(row, "html.parser").findAll("div", {"role" : "cell"})
            cells = row.find_all("div", {"role" : "cell"})
            url1 = cells[1].find('a')['href']
            print(url1)
                               
        finished = True

    breakpoint()
    # For each row in <div role="rowgroup">

        # For each cell in each row

    
    # If '>' button (next page of problems) is NOT disabled, click it and continue
    # Else, we're done

    pass


def is_logged_in(driver: WebDriver, wait: WebDriverWait) -> bool:
    # XPath query of the HTML for an 'isSignedIn' property that should be nested in a <script> tag
    return driver.execute_script("""
        return document.evaluate("//html[contains(., 'isSignedIn: true')]", 
            document, null, XPathResult.BOOLEAN_TYPE, null ).booleanValue;
    """)


def log_in(driver: WebDriver, wait: WebDriverWait):
    username = os.getenv('LEETCODE_USERNAME')
    password = os.getenv('LEETCODE_PASSWORD')

    if username and password:
        driver.get(LOGIN_URL)

        try:
            loading_is_finished = EC.invisibility_of_element((By.CLASS_NAME, "spinner"))
            wait.until(loading_is_finished)

            driver.find_element_by_name("login").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.find_element_by_id("signin_btn").click()
            #TODO improve this. page will hang forever if login fails and page never redirects.
            # data-is-error="true" if userid/password fields are blank
            # <p data-cy="sign-in-error" exists after failed login
            # Wait for page to redirect before finishing
            wait.until(EC.url_changes(LOGIN_URL))
        except TimeoutException:
            print("Timed out waiting for page to load")


if __name__ == "__main__":
    # execute only if run as a script
    main()