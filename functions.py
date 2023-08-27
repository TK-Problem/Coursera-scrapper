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

    # find html element
    _e = soup.find("title", string="Hours to complete")

    # if element found save results, else return empty string
    if _e:
        # move 3 parent levels above
        _e = _e.parent.parent.parent
        # get suggested completion time
        _suggested_t = _e.text[17:]
    else:
        _e = soup.find_all("div", {"class": "css-oj3vzs"})
        try:
            _suggested_t = _e[1].parent.text
        except AttributeError:
            _suggested_t = ''

    # find html element
    _e = soup.find("div", {"class": "_1fpiay2"})

    # if element found save results, else return empty string
    try:
        # get number of currently enrolled students
        _enrolled = _e.text
    except AttributeError:
        _e = soup.find_all("div", {"class": "css-oj3vzs"})
        try:
            _enrolled = _e[0].text.split("ratings ")[1]
        except AttributeError:
            _enrolled = ''

    # get scores
    _e = soup.find('span', {"data-test": 'number-star-rating'})

    # get specialization review count
    if _e:
        _ratings_score = _e.text
    else:
        _ratings_score = ''

    # select html element for description
    _e = soup.find("div", {"class": "cds-71 css-0 cds-73 cds-grid-item cds-118 cds-140"})

    # if element doesn't have text attribute select different section
    try:
        _description = _e.text
    except AttributeError:
        _e = soup.find_all("div", {"class": "rc-TogglableContent"})
        try:
            _description = _e[0].text
        except AttributeError:
            _description = ''
        except IndexError:
            _description = ''

    # add new information about specialization
    data_spec = line + [_suggested_t, _enrolled, _ratings_score, _description]

    # create empty list to store data
    data_courses = list()

    # find all courses
    courses = soup.find_all("div", {"class": "_jyhj5r CourseItem"})

    # iterate over courses elements
    for _course in courses:
        # get course number
        _course_no = _course.strong.parent.span.text

        # get course name
        _course_name = _course.find("h3", {"class": "headline-3-text bold m-t-1 m-b-2"}).text

        # some courses might not have ratings/reviews
        try:
            # get number of ratings
            _avg_ratings = _course.find("span", {"data-test": "number-star-rating"}).text
            _ratings_counts = _course.find("span", {"data-test": "ratings-count-without-asterisks"}).text
        except AttributeError:
            _ratings_counts = ""

        # get description
        _description = _course.find("div", {"class": "content-inner"}).text

        # get course href
        _href = _course.find("a", {"data-e2e": "course-link"})['href']

        # append list
        data_courses.append([line[-2], _course_no, _course_name, _ratings_counts, _description, _href])

    return data_spec, data_courses


def parse_course_page(html, line):
    """
    Returns list of lists with detailed information about weeks content
    :param html: string, raw html code from webdriver
    :param line: list, list of strings
    :return: list, list
    """
    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")

    # find all weeks with content
    week_contents = soup.find_all("div", {"class": "_jyhj5r SyllabusWeek"})

    # create empty list to store data
    data_week = list()
    data_lectures = list()

    # iterate over week contents
    for i, _c in enumerate(week_contents):
        # find expected duration
        try:
            # some pages don\t have duration provided
            _duration = _c.find("div", {"data-test": "duration-text-section"}).text.strip()[17:]
        except AttributeError:
            _duration = ''

        # get headline and description
        _name = _c.h3.text
        _description = _c.p.text

        # find syllabus details
        _syllabus = _c.find_all('div', {"class": 'ItemGroupView border-top p-t-2'})

        # iterate over elements
        for _s in _syllabus:
            # content type
            _c_type = _s.find('strong', {'class': '_1fe1gic7 m-x-1 learning-item'}).text.split(" ")[1]

            # find all lectures
            _lecture = _s.find_all("div", {"class": "_wmgtrl9 m-y-2"})

            # iterate over lectures contents
            for _l in _lecture:
                # check whatever information about duration exists
                try:
                    # get lecture duration
                    _d = _l.find('span', {"class": "duration-text m-x-1s"}).text
                except AttributeError:
                    # return empty string
                    _d = ""

                # check whatever information text available
                try:
                    # lecture text
                    _t = _l.text
                except AttributeError:
                    # substitute with empty string
                    _t = ''

                # append data
                if len(_d):
                    # add data to list
                    data_lectures.append([line[-1], i+1, _c_type, _t[:-1*len(_d)], _d])
                else:
                    data_lectures.append([line[-1], i+1, _c_type, _t, _d])

        # append list
        data_week.append([line[-1], i+1, _name, _duration, _description])

    return data_week, data_lectures

