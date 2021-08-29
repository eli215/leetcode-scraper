import os
import sys
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup, Tag
import re
import pyautogui

# Note: research logging best practices
# LOGFILE = "leetcode_scraper_log.txt"
BASE_URL = "https://leetcode.com"

def main():
    # Initial setup
    args = sys.argv[1:]
    load_dotenv()   # Load .env file
    DIRNAME = os.path.dirname(__file__)
    CHROMEDATA_DIR = os.path.join(DIRNAME, 'ChromeData')

    # Initialize webdriver
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROMEDATA_DIR}")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=60)

    driver.get(BASE_URL)
    # Log in to Leetcode if necessary
    if not is_logged_in(driver, wait):
        log_in(driver, wait)
    
    # Collect all problem URLs from problemset pages
    # Add to a JSON file
    update_problemset(driver, wait)

    # Loop through all problems

    # Navigate to problem URL
    # url = 'https://leetcode.com/problems/arranging-coins/'
    # driver.get(url)

    # has_solution = driver.execute_script("""
    #     return document.querySelector('[data-key="solution"]').getAttribute("data-disabled") == true;
    # """)

    # Modify Description page HTML w/ JS
    # - remove code window on right
    """
    var element = document.querySelector(".editor-wrapper__1ru6");
    if (element)
        element.parentNode.removeChild(element);
    """
    # - set left flexbox fill to '1' to fill page width
    # - if Solution exists, set its menu item href to our local copy

    # Scrape tags and add them to JSON file

    # Save Description page w/ right click Save As

    # Navigate to Solution URL (if applicable)

    # Modify page HTML w/ JS
    # - same stuff as above
    # - set Description menu item href to our local copy

    """
    title:
    number:
    url:
    filename:
    solution: {
        has_video:
    }
    acceptance:
    difficulty:
    frequency:
    tags: {

    }
    """
def update_problemset(driver: WebDriver, wait: WebDriverWait):
    """Scrape problemset data & write it to a JSON file."""

    PROBLEMSET_URL = "https://leetcode.com/problemset/all/"
    driver.get(PROBLEMSET_URL)

    finished = False
    data = []

    def parse_solution_type(cell: Tag) -> dict:
        """Determine solution type from cell html."""
        classname = cell.find('svg')['class']

        if "text-blue" in classname:  # article: "w-5 h-5 text-blue dark:text-dark-blue"
            return {'has_video' : False}
        if "text-purple" in classname:  # video: "w-5 h-5 text-purple dark:text-dark-purple"
            return {'has_video' : True}
        else:   # none: "w-5 h-5 text-gray-5 dark:text-dark-gray-5"
            return None

    # TODO: ensure view "100 / page" is selected from dropdown

    while not finished:
        table_html = driver.execute_script(
            """
                return document.querySelector('div[role="rowgroup"]').innerHTML;
            """
        )
        soup = BeautifulSoup(table_html, 'html.parser')
        # TODO: skip the first row of the first page somehow
        for i, row in enumerate(soup.find_all("div", {"role" : "row"})):
            cells = row.find_all("div", {"role" : "cell"})
            row_data = dict()
            row_data['url'] = BASE_URL + cells[1].find('a')['href']
            row_data['number'], row_data['title'] = cells[1].get_text().split('. ', 1)
            row_data['solution'] = parse_solution_type(cells[2])
            row_data['acceptance'] = float(cells[3].get_text()[:-1])
            row_data['difficulty'] = cells[4].get_text()
            row_data['frequency'] = float(cells[5].select('div[class*="bg-brand-orange"]')[0]['style'][7:-2])
            #row_data['tags'] = {}
            data.append(row_data)
            # breakpoint()

        # TODO: implement the following
        # If '>' button (next page of problems) is NOT disabled, click it and continue
        # Else, we're done              
        finished = True

    breakpoint()  


def is_logged_in(driver: WebDriver, wait: WebDriverWait) -> bool:
    """Check if browser session is currently signed in."""
    # XPath query of the HTML for an 'isSignedIn' property that should be nested in a <script> tag
    return driver.execute_script("""
        return document.evaluate("//html[contains(., 'isSignedIn: true')]", 
            document, null, XPathResult.BOOLEAN_TYPE, null ).booleanValue;
    """)


def log_in(driver: WebDriver, wait: WebDriverWait):
    """Log in using credentials in .env file."""
    LOGIN_URL = "https://leetcode.com/accounts/login"
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
            #TODO improve this. wait will timeout if login fails and page never redirects.
            # data-is-error="true" if userid/password fields are blank
            # <p data-cy="sign-in-error" exists after failed login
            # Wait for page to redirect before finishing
            wait.until(EC.url_changes(LOGIN_URL))
        except TimeoutException:
            # TODO: Handle this
            print("Timed out waiting for page to load")


if __name__ == "__main__":
    # execute only if run as a script
    main()