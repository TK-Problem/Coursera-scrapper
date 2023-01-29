from playwright.sync_api import sync_playwright
from functions import parse_specialization_page
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
    with open('specializations.csv', 'r', encoding='UTF8') as f:
        # reader object
        csv_reader = csv.reader(f)

        # skip header line and add it to new line
        scraped_data_spec = next(csv_reader)

        # add new headings
        scraped_data_spec += ["SuggestedTime", "Enrolled", "RecentViews", "Description"]
        scraped_data_spec = [scraped_data_spec]

        # create empty list to store info about courses
        scraped_data_courses = list()

        # convert to list so that tqdm can estimate finish time
        lines = [_line for _line in csv_reader]

        # iterate over lines
        for _line in tqdm(lines):
            # get website link (ignore first dash)
            _url = _line[-2][1:]

            # visit page
            page.goto("https://www.coursera.org/"+_url)

            # implicit wait 2 secs if show more button is present
            for i in range(2):
                # explicit wait
                time.sleep(1)
                # break loop if button is visible
                if page.locator("text=Show More").is_visible():
                    # click show more button
                    page.click("text=Show More", delay=50)
                    break

            # get html
            html = page.content()

            # parse html code
            data_spec, data_courses = parse_specialization_page(html, _line)

            # append detailed info about specialization course
            scraped_data_spec.append(data_spec)
            # append info about courses
            scraped_data_courses += data_courses

        # save detailed specialization courses data to.csv file
        with open('specializations_detailed.csv', 'w', encoding='UTF8', newline='') as f:
            # create writer object
            writer = csv.writer(f)

            # iterate over rows
            for row in scraped_data_spec:
                # save line
                writer.writerow(row)

        # save scrapped courses data to.csv file
        with open('courses.csv', 'w', encoding='UTF8', newline='') as f:
            # create writer object
            writer = csv.writer(f)

            # iterate over rows
            for row in scraped_data_courses:
                # save line
                writer.writerow(row)

