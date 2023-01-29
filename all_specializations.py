from playwright.sync_api import sync_playwright
from functions import parse_search_page
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

    # generate search url - search all products
    url = "https://www.coursera.org/search?index=prod_all_launched_products_term_optimization"
    # select only specializations filter
    url += "&entityTypeDescription=Specializations"

    # click search all courses
    page.goto(url)
    # small explicit wait to check that page is loading
    time.sleep(1)

    # implicit wait till clear filter loads
    while not page.locator("text=Clear all").is_visible():
        time.sleep(1)

    # get html
    html = page.content()

    # parse html code to extract information about specialization courses
    courses = parse_search_page(html)

    # record script start time
    start_time = time.time()

    # continue clicking button while next button is not disabled (100 is arbitrary chosen number)
    for i in range(100):
        # click next button
        page.click("button[data-track-component=pagination_right_arrow]", delay=50)

        # explicit wait till data loads (this also limits the request frequency)
        time.sleep(5)

        # get html
        html = page.content()

        # add new data
        courses += parse_search_page(html)

        # get next button class name
        _class_name = page.locator("button[data-track-component=pagination_right_arrow]").get_attribute('class')

        # break loop if class name changes to disabled
        if _class_name == "label-text box arrow arrow-disabled":
            break

    # return message how many pages were scrapped
    print(f"{i+2} pages with specialization courses scrapped in {time.time() - start_time:.2f} secs.")

    # header row values
    header_row = ["Specialization", "Instructors", "ReviewScore", "ReviewCount", "Skills", "Details", "URL", "ImgURL"]

    # save data to.csv file
    with open('specializations.csv', 'w', encoding='UTF8', newline='') as f:
        # create writer object
        writer = csv.writer(f)

        # add heading row
        writer.writerow(header_row)

        # iterate over rows
        for row in courses:
            # save line
            writer.writerow(row)
