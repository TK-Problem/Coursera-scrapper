from playwright.sync_api import sync_playwright
from tqdm import tqdm
from functions import parse_course_page
import time
import csv


# read data (first one needs to run all_specializations.py script to generate courses.csv file)
with open('courses.csv', 'r', encoding='UTF8') as f:
    # reader object
    csv_reader = csv.reader(f)

    # skip header line and add it to new line
    scraped_data_courses = next(csv_reader)

    # convert to list so that tqdm can estimate finish time
    csv_rows = [row for row in csv_reader]

# batch size
batch_size = 100

# read lines in batches of 100 (can be changed if needed)
for i in range(0, len(csv_rows), batch_size):
    # get lines
    _rows = csv_rows[i:i+batch_size]

    # create empty list to store all detailed course data
    _out_data = list()
    _out_lectures = list()

    # create webdriver for each batch of rows
    with sync_playwright() as p:
        # create webdriver (for debugging use headless False)
        browser = p.chromium.launch(headless=False, slow_mo=50)

        # create new page and visit coursera website
        page = browser.new_page()
        page.goto("https://www.coursera.org/")

        # click on cookie button
        page.click("button[id=onetrust-accept-btn-handler]", delay=50)

        # print status message
        print(f"Lines from {i} to {i+batch_size} are being processed.")

        # iterate over lines
        for _line in tqdm(_rows):
            # get website link (ignore first dash)
            _url = _line[-1][1:]

            # visit page
            page.goto("https://www.coursera.org/" + _url)

            # implicit wait 2 secs if show more button is present
            for _ in range(2):
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

            # process data
            data_week, data_lectures = parse_course_page(html, _line)

            # append data
            _out_data += data_week
            _out_lectures += data_lectures

        # save/append recorded lines to .csv files (detailed week)
        with open('weeks_basic.csv', 'a', encoding='UTF8', newline='') as f:
            # create writer object
            writer = csv.writer(f)

            # iterate over rows
            for _row in _out_data:
                # save line
                writer.writerow(_row)

        # save/append lecture data to.csv file
        with open('weeks_detailed.csv', 'a', encoding='UTF8', newline='') as f:
            # create writer object
            writer = csv.writer(f)

            # iterate over rows
            for _row in _out_lectures:
                # save line
                writer.writerow(_row)

    # count remaining batches
    _cnt = int(len(csv_rows) / batch_size) - i / batch_size - 1

    # status message how many batches are left
    print(f"{_cnt:.0f} batches left to process.")