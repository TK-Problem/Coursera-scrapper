from playwright.sync_api import sync_playwright
from tqdm import tqdm
import time
import csv


# main script
with sync_playwright() as p:
    # create webdriver (for debugging use headless False)
    browser = p.chromium.launch(headless=False, slow_mo=50)

    # create new page and visit coursera website
    page = browser.new_page()
    page.goto("https://www.coursera.org/")

    # click on cookie button
    page.click("button[id=onetrust-accept-btn-handler]", delay=50)

    # read data (first one needs to run all_specializations.py script to generate .csv file)
    with open('courses.csv', 'r', encoding='UTF8') as f:
        # reader object
        csv_reader = csv.reader(f)

        # skip header line and add it to new line
        scraped_data_courses = next(csv_reader)

        # convert to list so that tqdm can estimate finish time
        lines = [_line for _line in csv_reader]

        # iterate over lines
        for _line in tqdm(lines):
            # get website link (ignore first dash)
            _url = _line[-1][1:]

            # visit page
            page.goto("https://www.coursera.org/" + _url)

            # implicit wait 2 secs if show more button is present
            for i in range(2):
                # explicit wait
                time.sleep(1)
                # break loop if button is visible
                if page.locator("text=Show More").is_visible():
                    # click show more button
                    page.click("text=Show More", delay=50)
                    break

            # find all "See All" buttons
            _buttons = page.locator('span:has-text("See All")')

            # run condition while buttons can be found (exclude 2 last invisible buttons)
            while len(_buttons.all()) > 2:
                # click first button
                _buttons.all()[0].click(delay=50)

                # implicit wait between clicks
                time.sleep(0.2)

                # find all "See All" buttons
                _buttons = page.locator('span:has-text("See All")')

            # get html
            html = page.content()

