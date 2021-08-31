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
from selenium.webdriver.support.ui import Select
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

    # CSS selector constants & expected wait conditions
    PROBLEMSET_URL = "https://leetcode.com/problemset/all/"
    DROPDOWN_ID = 'headlessui-listbox-button-13'
    DROPDOWN_OPTION_CSS_SEL = f'ul[aria-labelledby="{DROPDOWN_ID}"] > li:last-of-type'  # last option is "100 / page"
    dropdown_option_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, DROPDOWN_OPTION_CSS_SEL))
    FIRST_ROW_CSS_SEL = 'div[role="rowgroup"] > div:first-of-type'
    first_row_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, FIRST_ROW_CSS_SEL))

    driver.get(PROBLEMSET_URL)

    
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

    # TODO: skip the first row of the first page somehow (if it's )
    # row1_is_special = 
    # var row1 = document.querySelector('div[role="rowgroup"] > div:first-of-type');
    # driver.find_element_by_css_selector(first_row_css_sel)
    """
    var element = document.querySelector(".editor-wrapper__1ru6");
    if (element)
        element.parentNode.removeChild(element);
    """

    # Make sure table size dropdown is set to view 100 problems per page
    tablesize_is_100 = driver.execute_script("""
        return document.querySelector('#headlessui-listbox-button-13').innerText == "100 / page";
        """)
    
    if not tablesize_is_100:
        driver.find_element_by_id(DROPDOWN_ID).click()
        wait.until(dropdown_option_clickable)
        driver.find_element_by_css_selector(DROPDOWN_OPTION_CSS_SEL).click()    
        wait.until(first_row_clickable)     # wait until table reloads

    breakpoint()
    has_next_page = True

    while has_next_page:
        table_contents = driver.execute_script(
            """
                return document.querySelector('div[role="rowgroup"]').innerHTML;
            """
        )
        soup = BeautifulSoup(table_contents, 'html.parser')

        for i, row in enumerate(soup.find_all('div', {'role' : "row"})):
            cells = row.find_all("div", {"role" : "cell"})
            row_data = dict()
            row_data['url'] = BASE_URL + cells[1].find('a')['href']
            row_data['number'], row_data['title'] = cells[1].get_text().split(". ", 1)
            row_data['solution'] = parse_solution_type(cells[2])
            row_data['acceptance'] = float(cells[3].get_text()[:-1])
            row_data['difficulty'] = cells[4].get_text()
            row_data['frequency'] = float(cells[5].select('div[class*="bg-brand-orange"]')[0]['style'][7:-2])
            #row_data['tags'] = {}
            data.append(row_data)

        next_btn_css_sel = 'nav[role="navigation"] > button:last-of-type'
        has_next_page = not driver.execute_script(
            f"""
                return document.querySelector('{next_btn_css_sel}').hasAttribute("disabled")
            """
        )

        if has_next_page:
            try:
                next_btn_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, next_btn_css_sel))
                wait.until(next_btn_clickable)
                driver.find_element_by_css_selector(next_btn_css_sel).click()
                # TODO: wait for table element to be clickable to indicate next page has loaded

            except TimeoutException:
              pass  
        
        # <nav role="navigation" class="mb-6 md:mb-0 flex flex-nowrap items-center space-x-2">
        # If '>' button (next page of problems) is NOT disabled, click it and continue
        # Else, we're done              


        breakpoint()  


def is_logged_in(driver: WebDriver, wait: WebDriverWait) -> bool:
    """Check if browser session is currently signed in."""
    # XPath query of the HTML for an 'isSignedIn' property that should be nested in a <script> tag
    return driver.execute_script("""
        return document.evaluate("//html[contains(., 'isSignedIn: true')]", 
            document, null, XPathResult.BOOLEAN_TYPE, null ).booleanValue;
    """)


def log_in(driver: WebDriver, wait: WebDriverWait):
    """Log in using credentials from .env file."""
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