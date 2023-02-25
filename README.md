## Coursera website scrapper

This is a project created specifically for the purpose of downloading locally available statistics on Coursera courses and their reviews. The scraping code used in this project was inspired by the following tutorial:

[![IMAGE_ALT](https://img.youtube.com/vi/H2-5ecFwHHQ/0.jpg)](https://www.youtube.com/watch?v=H2-5ecFwHHQ)


## Script order

To re-scrape the most recent data about Coursera courses and reviews, run the following scripts in the specified order:

1. Run `python all_specializations.py` first. This will create a new file called `specializations.csv`;
2. To obtain more detailed information about specializations, run `python specialization_detailed.py`. This will create a new file called `specializations_detailed.csv`;
3. To obtain more detailed information about courses within a specialization, run `python course_detailed.py`. This will create two new files, `courses_detailed.csv` and `weeks_detailed.csv`;
4. Read the latest reviews in the Google Colab notebook `coursera_review_scraper.ipynb`. To prevent your home IP from being blocked, it is recommended that you use a Google virtual machine to read the latest reviews in the Google Colab notebook.