from playwright.sync_api import sync_playwright
from functions import parse_course_page
import csv


# main script
with sync_playwright() as p:
    # create webdriver (for debugging use headless False)
    browser = p.chromium.launch(headless=False, slow_mo=50)

    # create new page and visit coursera website
    page = browser.new_page()
    page.goto("https://www.coursera.org/")

    # click on cookie button
    page.click("button[id=onetrust-accept-btn-handler]")

    # generate search url
    # search all products
    url = "https://www.coursera.org/search?index=prod_all_launched_products_term_optimization"
    # select only specializations
    url += "&entityTypeDescription=Specializations"
    # select only english language
    url += "&allLanguages=English"

    # click search all courses
    page.goto(url)

    # get html
    html = page.content()

    # parse html code to extract information about specialization courses
    courses = parse_course_page(html)

    # save data to.csv file
    with open('specialziations.csv', 'w', encoding='UTF8', newline='') as f:
        # create writer object
        writer = csv.writer(f)

        # iterate over rows
        for row in courses:
            # save line
            writer.writerow(row)

