from playwright.sync_api import sync_playwright
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
    with open('specializations.csv', 'r') as f:
        # reader object
        csv_reader = csv.reader(f)

        # iterate over lines
        for line in csv_reader:
            # get website link (ignore first dash)
            _url = line[-2][1:]

            # visit page
            page.goto("https://www.coursera.org/"+_url)

            # implicit wait 5 secs if show more button is present
            for i in range(5):
                # break loop if button is visible
                if page.locator("text=Show More").is_visible():
                    # click show more button
                    page.click("text=Show More", delay=50)
                    break
                # explicit wait
                time.sleep(1)
