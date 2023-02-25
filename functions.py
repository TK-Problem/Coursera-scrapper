"""
Helper functions to parse html code with BeautifulSoup soup library
"""
from bs4 import BeautifulSoup


def parse_search_page(html):
    """
    Returns list of lists with information about specialization courses from search query
    :param html: string, raw html code from webdriver
    :return: list
    """
    # convert to bs4 object
    soup = BeautifulSoup(html, "html.parser")

    # find all courses in page
    courses = soup.find_all("li", {"class": "cds-71 css-0 cds-73 cds-grid-item cds-118 cds-126 cds-138"})

    # create empty list to store output data
    data = list()

    # iterate over course elements and save required information
    for _course in courses:
        # get main element
        _info = _course.find('a')

        # get course name
        _course_name = _info.find("h2", {"class": "cds-33 css-bku0rr cds-35"}).text

        # course instructor name
        _instructor = _info.find("span", {"class": "cds-33 css-2fzscr cds-35"}).text

        # some specialization courses don't have reviews
        try:
            # review stats
            _review_score = _info.find("p", {"class": "cds-33 css-zl0kzj cds-35"}).text
            _reviews_stats = _info.find("p", {"class": "cds-33 css-14d8ngk cds-35"}).text
        except AttributeError:
            # return empty string
            _review_score = ""
            _reviews_stats = ""

        # some specialization courses don't have listed skills
        try:
            # skills to gain
            _skills = _info.find("p", {"class": "cds-33 css-5or6ht cds-35"}).text[20:]
        except AttributeError:
            # return empty string
            _skills = ''

        # course details
        _details = _info.find_all("p", {"class": "cds-33 css-14d8ngk cds-35"})[-1].text

        # some specialization courses don't have image
        try:
            # get image source
            _img_url = _info.find("div", {"class": "css-1doy6bd"}).find("img")["src"]
        except KeyError:
            # return empty string
            _img_url = ''

        # get link to specialization course
        _href = _info['href']

        # append list
        data.append([_course_name, _instructor, _review_score, _reviews_stats, _skills, _details, _href, _img_url])

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
        _suggested_t = ""

    # find html element
    _e = soup.find("div", {"class": "_1fpiay2"})

    # if element found save results, else return empty string
    if _e:
        # get number of currently enrolled students
        _enrolled = _e.text
    else:
        _enrolled = ""

    # find html element
    _e = soup.find("div", {"data-e2e": "description"})

    # if element found save results, else return empty string
    if _e:
        # specialization description
        _description = _e.text
    else:
        _description = ""

    # add new information about specialization
    data_spec = line + [_suggested_t, _enrolled, _description]

    # create empty list to store data
    data_courses = list()

    # find all courses
    courses = soup.find_all("div", {"class": "_jyhj5r CourseItem"})

    # iterate over courses elements
    for _course in courses:
        # get course number
        _course_no = _course.find("span", {"class": "_1nc68rjl text-secondary d-block m-y-1"}).text
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

