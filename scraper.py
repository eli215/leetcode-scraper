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
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup, Tag
import json
import re
import pyautogui

# Note: research logging best practices
# LOGFILE = "leetcode_scraper_log.txt"
BASE_URL = "https://leetcode.com"
JSON_FILENAME = "problemset.json"
JSON_ROOT_ELEMENT_NAME = "problemset"

def main():
    # Initial setup
    args = sys.argv[1:]
    use_existing_problemset_file = True    # TODO: setup CLI arg
    load_dotenv()   # Load .env file
    DIRNAME = os.path.dirname(os.path.realpath(sys.argv[0]))
    CHROMEDATA_DIR = os.path.join(DIRNAME, "ChromeData")
    DOWNLOAD_DIR = os.path.join(DIRNAME, "problems")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Initialize webdriver
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROMEDATA_DIR}")
    options.add_argument('--save-page-as-mhtml')
    options.add_argument("--start-maximized")
    prefs = {
            # "profile.default_content_settings.popups": 0,
            'download.default_directory' : f"{DOWNLOAD_DIR}",
            'directory_upgrade': True
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=20)

    driver.get(BASE_URL)
    # Log in to Leetcode if necessary
    if not is_logged_in(driver, wait):
        log_in(driver, wait)
    
    # Collect all problem URLs from problemset pages
    # Add to a JSON file
    problemset = dict()
    if use_existing_problemset_file:
        with open(JSON_FILENAME, 'r', encoding='utf-8') as jsonfile:
            problemset = json.load(jsonfile)['problemset']
    else:
        problemset = get_problemset(driver, wait)

    # Loop through all problems
    first = True
    for problem in problemset.values():
        if first:
            first = False
            continue
        get_problem(driver, wait, problem)
    # Navigate to problem URL
    # url = 'https://leetcode.com/problems/arranging-coins/'
    # driver.get(url)

    # has_solution = driver.execute_script("""
    #     return document.querySelector('[data-key="solution"]').getAttribute("data-disabled") == true;
    # """)

def get_problem(driver: WebDriver, wait: WebDriverWait, problem: dict()) -> dict():

    driver.get(problem['url'])
    try:
        loading_is_finished = EC.invisibility_of_element((By.CLASS_NAME, "spinner"))
        wait.until(loading_is_finished)
        
        # Modify Description page HTML w/ JS
        # Remove code window on right
        CODE_EDITOR_CSS_SEL = ".editor-wrapper__1ru6"
        driver.execute_script(f"""
            var element = document.querySelector("{CODE_EDITOR_CSS_SEL}");
            if (element)
                element.parentNode.removeChild(element);
        """)
    
        # Expand description flexbox to fill page width
        DESCRIPTION_WRAPPER_CSS_SEL = ".side-tools-wrapper__1TS9"
        DESCRIPTION_WRAPPER_NEW_STYLE = "overflow: hidden; flex: 1 1 auto;"
        driver.execute_script(f"""
            document.querySelector("{DESCRIPTION_WRAPPER_CSS_SEL}").setAttribute('style', "{DESCRIPTION_WRAPPER_NEW_STYLE}");
        """)

        # Expand boxes (Companies, Tags, Hints, etc.)
        EXTRA_SECTIONS_CSS_SEL = '.css-1jqueqk [class^="header__"]'
        MORE_BTN_CSS_SEL = ".btn__1z2C.btn-md__M51O.show-more__2LD1"

        # Click them bottom-up, otherwise downward expansion messes with subsequent clicks.
        for section in reversed(driver.find_elements_by_css_selector(EXTRA_SECTIONS_CSS_SEL)):

            section_class = section.get_attribute('class')
            section_clickable = EC.element_to_be_clickable((By.CLASS_NAME, section_class))
            wait.until(section_clickable)
            section.click()
        
        # If there are any "More" buttons, expand their contents
        # Note: I've only ever seen one 'More' button (under Companies). Make a loop if more show up.
        more_btns = driver.find_elements_by_css_selector(MORE_BTN_CSS_SEL)
        if more_btns:
            more_btn_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, MORE_BTN_CSS_SEL))
            wait.until(more_btn_clickable)
            more_btns[0].click()
        
        # 
        padded_prob_num = f"{problem['number']:04}"
        hyphenated_prob_name = f"{problem['url'][problem['url'].rfind('/')+1:]}"
        problem_filename = f"{padded_prob_num}_{hyphenated_prob_name}.mhtml"

        save_page(problem_filename)
        breakpoint()
        if None is not problem['solution']:
            solution_filename = f"{padded_prob_num}_solution_{hyphenated_prob_name}.mhtml"

            # TODO: change solution href to solution_filename
            # soup = BeautifulSoup

        # Note: just discovered that the href changes can't be done in the browser:
        # the base URI defaults to https://leetcode.com even when I explicitly change it.
        # TODO: (after other in-browser changes)
        # - download .mhtml
        # - open file w/ bs4
        # - make href edits, directing links to our local copy
        #   - first, add "<base href="~/" />" inside of <head>.
        #   - then change href values where needed, using "../" for relative path
        # SOLUTION_HREF_CSS_SEL = "div[data-key='solution'] > a:first-child"
        # driver.execute_script(f"""
        #     document.querySelector("{SOLUTION_HREF_CSS_SEL}").setAttribute('href', "overflow: hidden; flex: 1 1 auto;");    
        # """)
        """
        <script type="text/javascript">
        document.getElementsByTagName('head')[0].setAttribute('href', "../");
        alert("yoo");
        </script>
        """

        # - direct Next button to local file

        # TODO: Scrape tags and add them to JSON file

        # Save Description page w/ right click Save As

        # Navigate to Solution URL (if applicable)

        # Modify page HTML w/ JS
        # - same stuff as above
        # - set Description menu item href to our local copy
    except TimeoutException:
        print(f"Timed out while getting problem #{problem['number']}.")
    
    breakpoint()
    return dict()


def save_page(filename: str) -> None:
    pyautogui.hotkey('ctrl', 's')



def get_solution(driver: WebDriver, wait: WebDriverWait, problem: dict()) -> None:
    """Modify and download the solution to the given problem."""
    pass


def get_problemset(driver: WebDriver, wait: WebDriverWait) -> dict:
    """Scrape problemset data & write it to a JSON file."""

    PROBLEMSET_URL = "https://leetcode.com/problemset/all/"
    driver.get(PROBLEMSET_URL)

    def parse_solution_type(cell: Tag) -> dict:
        """Determine solution type from cell html."""
        classname = cell.find('svg')['class']

        if "text-blue" in classname:  # article: "w-5 h-5 text-blue dark:text-dark-blue"
            return {'has_video' : False}
        if "text-purple" in classname:  # video: "w-5 h-5 text-purple dark:text-dark-purple"
            return {'has_video' : True}
        else:   # none: "w-5 h-5 text-gray-5 dark:text-dark-gray-5"
            return None

    # Make sure table size dropdown is set to view 100 problems per page 
    TABLE_CSS_SEL = 'div[role="rowgroup"]'
    FIRST_ROW_CSS_SEL = f'{TABLE_CSS_SEL} > div:first-of-type'
    DROPDOWN_ID = 'headlessui-listbox-button-13'

    # TODO: skip first item if it's a LeetCode sponsored question (wrong url)
    tablesize_setting = int(driver.execute_script(f"""
        return document.querySelector('#{DROPDOWN_ID}').innerText;
    """)[:-7])      # trim " / page"

    first_row_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, FIRST_ROW_CSS_SEL))

    if tablesize_setting != 100:
        DROPDOWN_OPTION_CSS_SEL = f'ul[aria-labelledby="{DROPDOWN_ID}"] > li:last-of-type'  # last option is "100 / page"
        dropdown_option_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, DROPDOWN_OPTION_CSS_SEL))
        try:
            driver.find_element_by_id(DROPDOWN_ID).click()
            wait.until(dropdown_option_clickable)
            driver.find_element_by_css_selector(DROPDOWN_OPTION_CSS_SEL).click()    
            wait.until(first_row_clickable)     # wait until table reloads
            # update tablesize value?
        except TimeoutException:
            print("Timed out while changing table size.")

    data = dict()
    on_final_page = False
    while not on_final_page:
        table_contents = driver.execute_script(f"""
            return document.querySelector('{TABLE_CSS_SEL}').innerHTML;
        """)
        soup = BeautifulSoup(table_contents, 'html.parser')

        for i, row in enumerate(soup.find_all('div', {'role' : "row"})):
            cells = row.find_all("div", {"role" : "cell"})
            row_data = dict()

            # added 'number' back temporarily while I decide what to do
            row_data['number'], 
            row_data['title'] = cells[1].get_text().split(". ", 1)
            row_data['number'] = int(row_data['number'])
            # number = int(number)
            row_data['url'] = BASE_URL + cells[1].find('a')['href'].removesuffix('/')
            row_data['solution'] = parse_solution_type(cells[2])
            row_data['acceptance'] = float(cells[3].get_text()[:-1])
            row_data['difficulty'] = cells[4].get_text()
            row_data['frequency'] = float(cells[5].select('div[class*="bg-brand-orange"]')[0]['style'][7:-2])

            data[row_data['number']] = row_data

        NEXT_BTN_CSS_SEL = 'nav[role="navigation"] > button:last-of-type'
        on_final_page = driver.execute_script(f"""
            return document.querySelector('{NEXT_BTN_CSS_SEL}').hasAttribute("disabled")
        """)

        if not on_final_page:
            try:
                # Navigate to next page
                next_btn_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_BTN_CSS_SEL))
                wait.until(next_btn_clickable)
                driver.find_element_by_css_selector(NEXT_BTN_CSS_SEL).click()

                DIV_CONTAINING_TABLE_CSS_SEL = 'div[class="-mx-4 md:mx-0 opacity-50 pointer-events-none"]'
                table_loading = EC.presence_of_element_located((By.CSS_SELECTOR, DIV_CONTAINING_TABLE_CSS_SEL))
                wait.until(table_loading)   # table is loading
                wait.until_not(table_loading)   # table is finished loading
            except TimeoutException:
              print("Timed out while loading next page of problemset.")            

    # Write data to JSON file 
    with open(JSON_FILENAME, mode='w', encoding='utf-8') as file:
        json.dump({f"{JSON_ROOT_ELEMENT_NAME}" : data}, file)
    
    return data  


def is_logged_in(driver: WebDriver, wait: WebDriverWait) -> bool:
    """Check if browser session is currently signed in."""
    # XPath query of the HTML for an 'isSignedIn' property that should be nested in a <script> tag
    return driver.execute_script("""
        return document.evaluate("//html[contains(., 'isSignedIn: true')]", 
            document, null, XPathResult.BOOLEAN_TYPE, null ).booleanValue;
    """)


def log_in(driver: WebDriver, wait: WebDriverWait) -> None:
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