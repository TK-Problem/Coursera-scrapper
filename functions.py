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
    _e = soup.find("div", {"class": "rc-ProductMetrics"})

    # if element found save results, else return empty string
    if _e:
        # get recent views count
        _recent_views = _e.text
    else:
        _recent_views = ""

    # find html element
    _e = soup.find("div", {"data-e2e": "description"})

    # if element found save results, else return empty string
    if _e:
        # specialization description
        _description = _e.text
    else:
        _description = ""

    # add new information about specialization
    data_spec = line + [_enrolled, _recent_views, _suggested_t, _description]

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
