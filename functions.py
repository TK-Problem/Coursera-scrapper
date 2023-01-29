"""
Helper functions to parse html code with BeautifulSoup soup library
"""
from bs4 import BeautifulSoup


def parse_course_page(html):
    """
    Returns list of lists with information about specialization course
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

        # review stats
        _review_score = _info.find("p", {"class": "cds-33 css-zl0kzj cds-35"}).text
        _reviews_stats = _info.find("p", {"class": "cds-33 css-14d8ngk cds-35"}).text

        # skills to gain
        _skills = _info.find("p", {"class": "cds-33 css-5or6ht cds-35"}).text[20:]

        # course details
        _details = _info.find_all("p", {"class": "cds-33 css-14d8ngk cds-35"})[-1].text

        # get image source
        _img_url = _info.find("div", {"class": "css-1doy6bd"}).find("img")["src"]

        # get link to specialization course
        _href = _info['href']

        # append list
        data.append([_course_name, _instructor, _review_score, _reviews_stats, _skills, _details, _href, _img_url])

    # return list of lists (each element has information about specialization course)
    return data
