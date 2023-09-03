from playwright.sync_api import sync_playwright
from tqdm import tqdm
from functions import parse_course_page
import csv


# batch size
BATCH_SIZE = 100

# read data (first one needs to run all_specializations.py script to generate courses.csv file)
with open('courses.csv', 'r', encoding='UTF8') as f:
    # reader object
    csv_reader = csv.reader(f)

    # skip header line and add it to new line
    scraped_data_courses = next(csv_reader)

    # convert to list so that tqdm can estimate finish time
    csv_rows = [row for row in csv_reader]

# read lines in batches of 100 (can be changed if needed)
for i in range(0, len(csv_rows), BATCH_SIZE):
    # get lines
    _rows = csv_rows[i:i+BATCH_SIZE]

    # create empty list to store all detailed course data
    if i > 0:
        data_week = list()
        data_lectures = list()
        data_course_detailed = list()
    else:
        # write header rows
        data_week = [["CourseURL", "ModuleNo", "ModuleName", "Time2Complete", "ContentsSummary"]]
        data_lectures = [["CourseURL", "ModuleNo", "Type", "LectureName"]]
        data_course_detailed = [["CourseURL", "CourseLevel", "Time2Complete",
                                 "ReviewsCnt", "RatingScore", "Enrolled", "CourseDescription"]]

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
        print(f"Lines from {i} to {i+BATCH_SIZE} are being processed.")

        # iterate over lines
        for _line in tqdm(_rows):
            # get website link (ignore first dash)
            _url = _line[1][1:]

            # visit page
            page.goto("https://www.coursera.org/" + _url)

            # get html
            html = page.content()

            # process data
            _data_course_detailed, _data_week, _data_lectures = parse_course_page(html, _line[1])

            # append data
            data_week += _data_week
            data_lectures += _data_lectures
            data_course_detailed.append(_data_course_detailed)

    # save/append recorded lines to .csv files (detailed week)
    with open('weeks.csv', 'a', encoding='UTF8', newline='') as f:
        # create writer object
        writer = csv.writer(f)

        # iterate over rows
        for _row in data_week:
            # save line
            writer.writerow(_row)

    # save/append lecture data to.csv file
    with open('weeks_detailed.csv', 'a', encoding='UTF8', newline='') as f:
        # create writer object
        writer = csv.writer(f)

        # iterate over rows
        for _row in data_lectures:
            # save line
            writer.writerow(_row)

    # save/append lecture data to.csv file
    with open('courses_detailed.csv', 'a', encoding='UTF8', newline='') as f:
        # create writer object
        writer = csv.writer(f)

        # iterate over rows
        for _row in data_course_detailed:
            # save line
            writer.writerow(_row)

    # count remaining batches
    _cnt = int(len(csv_rows) / BATCH_SIZE) - i / BATCH_SIZE - 1

    # status message how many batches are left
    print(f"{_cnt:.0f} batches left to process.")