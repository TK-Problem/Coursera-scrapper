from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


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

    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")


