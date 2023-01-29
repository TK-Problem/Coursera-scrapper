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
        scraped_data = next(csv_reader)

        # add new headings
        scraped_data += ["SuggestedTime", "Enrolled", "RecentViews", "Description"]
        scraped_data = [scraped_data]

        # convert to list (so that tqdm can estimate end time)
        lines = [_line for _line in csv_reader]

        # iterate over lines
        for _line in tqdm(lines):
            # get website link (ignore first dash)
            _url = _line[-2][1:]

            # visit page
            page.goto("https://www.coursera.org/"+_url)

            # implicit wait 3 secs if show more button is present
            for i in range(3):
                # break loop if button is visible
                if page.locator("text=Show More").is_visible():
                    # click show more button
                    page.click("text=Show More", delay=50)
                    break

                # explicit wait
                time.sleep(1)

            # get html
            html = page.content()

            # parse html code and append to all data
            scraped_data.append(parse_specialization_page(html, _line))

        # save data to.csv file
        with open('specializations_detailed.csv', 'w', encoding='UTF8', newline='') as f:
            # create writer object
            writer = csv.writer(f)

            # iterate over rows
            for row in scraped_data:
                # save line
                writer.writerow(row)
