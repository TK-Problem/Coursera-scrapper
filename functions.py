"""
Helper functions to parse html code with BeautifulSoup soup library
"""
from bs4 import BeautifulSoup
import re


def parse_search_page(html):
    """
    Returns list of lists with information about specialization courses from search query
    :param html: string, raw html code from webdriver
    :return: list
    """
    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")

    # find all courses in page
    courses = soup.find_all("li", {"class": "cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76"})

    # create empty list to store output data
    data = list()

    # iterate over course elements and save required information
    for _course in courses:
        # get main element
        _info = _course.find('a')

        # get course description
        _description = _info['aria-label']

        # get link to specialization course/professional certificate
        _href = _info['href']

        """
        extract important data
        """
        # course type, either "professional-certificates" or "specializations"
        _course_type = _href.split("/")[1]
        # course name
        _by_idx = _description.index(" by")
        _course_name = _description[:_by_idx]

        # find course instructor name
        _instructor = re.search(r'by\s(.*?),', _description)
        if _instructor:
            _instructor = _instructor.group(1)
        else:
            _instructor = ""

        # count review stars
        _stars = re.findall(r'(\d+\.\d+\s*stars)', _description)
        if _stars:
            _stars = _stars[0]
        else:
            _stars = ""

        # get number of reviews
        _reviews = re.search(r'by\s([\d\.]+)([kM]?)\s*reviews', _description)
        if _reviews:
            number_part = _reviews.group(1)
            multiplier = _reviews.group(2)
            if multiplier == 'k':
                _reviews = int(float(number_part) * 1_000)
            elif multiplier == 'M':
                _reviews = int(float(number_part) * 1_000_000)
            else:
                _reviews = int(number_part)
        else:
            _reviews = ""

        # append list
        data.append([_course_name, _instructor, _reviews, _stars, _course_type, _href, _description])

    # return list of lists (each element has information about specialization course)
    return data


def parse_specialization_page(html, line):
    """
    Returns list of lists with detailed information about specialization course
    :param html: string, raw html code from webdriver
    :param line: list, list of strings
    :return: list, list
    """
    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")

    """
    specializations_detailed.csv section
    """

    # course info
    _info = soup.find_all("section", {"class": "css-3nq2m6"})

    # check if information is available (element is found)
    if _info:
        # find basic info
        _spec_info = _info[0].find_all("div", {"class": "cds-119 css-h1jogs cds-121"})

        # generate stock info
        _level = ""
        _suggested_t = ""
        _ratings_score = ""
        if "." in _spec_info[0].text:
            _ratings_score = _spec_info[0].text

        for _ in _spec_info:
            _text = _.text
            if "level" in _text:
                _level = _text
            elif "week" in _text:
                _suggested_t = _text

        # get suggested completion time
        _reviews = _info[0].find_all("p", {"class": "cds-119 css-dmxkm1 cds-121"})
        if _reviews:
            _reviews = _reviews[0].text
        else:
            _reviews = ""
    else:
        # because this element is not found, no information can be retried for the following variables
        _level = ""
        _suggested_t = ""
        _reviews = ""
        _ratings_score = ""

    # get number on enrolled students
    _enrolled = ""
    for _e in soup.find_all("p", {"class": "cds-119 css-80vnnb cds-121"}):
        if "enrolled" in _e.text:
            _enrolled = _e.text

    # get other info
    _description = soup.find_all("div", {"class": "cds-9 css-0 cds-11 cds-grid-item cds-56 cds-79 cds-94"})
    if _description:
        _description = _description[0].text
    else:
        _description = ""

    # add new information about specialization
    data_spec = line + [_level, _suggested_t, _reviews, _ratings_score, _enrolled, _description]

    """
    courses.csv section
    """

    # find all courses
    courses = soup.find_all("button", {"class": "cds-149 cds-button-disableElevation css-of9un"})

    # create empty list to store all data about courses
    data_courses = list()

    for _course in courses:
        # get contents
        _contents = _course.parent

        # get information
        _course_name = _contents.h3.text
        _course_html = _contents.a['href']

        # get additional info
        _info = _contents.find("div", {'class': 'cds-119 css-mc13jp cds-121'}).find_all('span')
        _course_no = _info[0].text
        if len(_info) > 2:
            _course_time = _info[2].text
        else:
            _course_time = ""

        if len(_info) > 5:
            _course_score = _info[-3].text
            _course_review_cnt = _info[-1].text
        else:
            _course_score = ""
            _course_review_cnt = ""

        # add information about courses
        data_courses.append(line + [_course_html, _course_name, _course_no,
                                    _course_time, _course_score, _course_review_cnt])

    return data_spec, data_courses


def parse_course_page(html, line):
    """
    Returns list of lists with detailed information about weeks content
    :param html: string, raw html code from webdriver
    :param line: list, list of strings
    :return: list, list, list
    """
    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")

    # find all weeks with content
    week_contents = soup.find_all("div", {"data-testid": "accordion-item"})

    # create empty list to store data
    data_course_detailed = list()
    data_week = list()
    data_lectures = list()

    # iterate over week contents
    for i, _c in enumerate(week_contents):
        # check whatever button has information about week
        _week_summary = _c.find_all("div", {"class": "cds-119 css-mc13jp cds-121"})
        if _week_summary:
            # get basic week info
            _week_name = _c.h3.text
            _week_summary = _week_summary[0].find_all("span")
            _week_no = _week_summary[0].text
            if len(_week_summary) > 2:
                _time2complete = _week_summary[2].text
            else:
                _time2complete = ""

            # get overview info
            _week_contents = _c.find_all("div", {"class": "css-15ko5n9"})
            _overview = []

            # iterate over lectures
            for _w in _week_contents:
                # get main week info
                _overview.append(_w.h5.text.replace("•", " "))
                # find all lectures
                _lectures = _w.find_all("li", {"class": "cds-119 css-1y4i2uq cds-121"})
                # iterate over all lectures
                for _l in _lectures:
                    # get lecture contents
                    _lec_contents = _l.text.replace("•", " ").replace("Preview module", "")
                    data_lectures.append([line, _week_no, _w.h5.text.replace("•", " ").split(" ")[1], _lec_contents])

            # add information about courses
            data_week.append([line, _week_no, _week_name, _time2complete, " | ".join(_overview)])

        else:
            # other buttons are unimportant, can close loop
            break

    return data_course_detailed, data_week, data_lectures

