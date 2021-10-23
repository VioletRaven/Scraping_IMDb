from selenium import webdriver
from bs4 import BeautifulSoup
import time
import datetime
import calendar
import sqlite3
import pandas as pd

'''
La funzione `start_driver()` crea un driver per il browser Chrome.
Assegna una directory (che deve essere precedentemente creata per il salvataggio dei cookie 
e delle informazioni utente per eventuali login a pagine web
Infine imposta il path al *chromedriver* che può essere assoluto o relativo.
'''


#some films need to be specified in Italian --> maybe because the webdriver has italian settings

films = {'fifties_films' : ['Peter pan', 'Alice nel paese delle meraviglie', 'Cenerentola'], 'fifties_years':[1953, 1951,1950]
         , 'sixties_films' : ['The Sword in the Stone', 'The Jungle Book', 'Mary Poppins'], 'sixties_years':[1963, 1967, 1964]
         , 'seventies_films' : ['The Aristocats', 'Robin Hood', 'The Many Adventures of Winnie the Pooh'], 'seventies_years':[1970, 1973, 1977]
         , 'eighties_films' : ['The Little Mermaid', 'Tron', 'Oliver & Company'], 'eighties_years':[1989, 1982, 1988]
         , 'nineties_films' : ['Aladdin', 'The Lion King', 'Hercules'], 'nineties_years':[1992, 1994, 1997]
         , 'twothousand_films' : ["The Emperor's New Groove", 'Monsters, Inc.', 'Lilo & Stitch'], 'twothousand_years':[2000, 2001, 2002]
         , 'twothousandten_films' : ['Tangled', 'Brave', 'Frozen'], 'twothousandten_years':[2010, 2012, 2013]}

#films.get('fifties_films')[0] # get film
#films.get('fifties_years')[0] # get year

# get film names and years from vocabulary
film_names = [films.get(i) for i in films if i.split('_')[1] == 'films']
film_years = [films.get(i) for i in films if i.split('_')[1] == 'years']

#flatten the list
film_names = [film for sublist in film_names for film in sublist]
film_years = [years for sublist in film_years for years in sublist]

def start_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(r'C:\Users\Mario\Desktop')
    chrome_options.add_argument(r'--profile-directory=Default')
    driver = webdriver.Chrome(
        executable_path="C:/Users/Mario/Desktop/Selenium/chromedriver.exe",
        options=chrome_options)

    return driver

def get_review_page(title, year):
    driver = start_chrome_driver()
    driver.get('https://www.imdb.com/')
    text = str(title)
    search = driver.find_element_by_id("suggestion-search")
    for letter in text:
        search.send_keys(letter)
        time.sleep(.1)
    button = driver.find_element_by_id("suggestion-search-button")
    button.click()

    #avoid homonymous element by specifying year
    diff_movies = driver.find_elements_by_class_name('result_text')
    movie = 0
    for n, i in enumerate(diff_movies):
        if str(year) in i.text:
            movie += n
    button = diff_movies[movie]
    
    #get href button by xpath and enter movie page
    button = button.find_element_by_xpath('//*[@id="main"]/div/div[2]/table/tbody/tr[3]/td[2]/a')
    button.click()

    #find reviews
    new_button = driver.find_element_by_xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/ul/li[1]/a')
    new_button.click()

    #load all reviews

    more = driver.find_element_by_id("load-more-trigger")
    while more.is_displayed():
        print('loading...\n')
        more.click()
        time.sleep(2)
        more = driver.find_element_by_id("load-more-trigger")

    #load "warning spoilers"

    warnings = driver.find_elements_by_class_name("spoiler-warning__control")
    i = 1
    for warning in warnings:
        print("clicking warning n° {}".format(i), end=",\n")
        warning.click()
        time.sleep(1)
        i += 1

    html = driver.page_source
    driver.quit()

    return html

#function needed for good formatting when saving as datetime object
def month_changer(date):
    month = date.split(' ')[1]
    month_num = datetime.datetime.strptime(month, '%B').month
    month_name = calendar.month_abbr[month_num]
    return date.split(' ')[0] + ' ' + month_name + ' ' + date.split(' ')[2]

def create_db(path, conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS disney (
        film_name           TEXT,
        film_year           INTEGER,
        author_name         TEXT,
        review_date         TEXT,
        score               INTEGER,
        title_name          TEXT,
        review_text         TEXT,
        POU                 INTEGER
    );
    """)
    conn.commit()

def beauty_parser(html_page, film_, year_, conn):

    # loop to parse through reviews and populate dataset

    # parsing html page
    soup = BeautifulSoup(html_page, "html.parser")
    reviews = soup.find_all("div", {"class": "lister-item"})

    imdb_df = pd.DataFrame(columns=['film_name', 'film_year', 'author_name', 'review_date',
                                    'score', 'title_name', 'review_text', 'POU'])

    for review in reviews:
        # get rating
        rating = review.find("span", {"class": "rating-other-user-rating"})
        rating = 0 if rating is None else int(rating.text.strip().split("/")[0])

        # get title
        title = review.find("a", {"class": "title"})
        title = 'NA' if title is None else title.text.strip()

        # get review

        review_data = review.find('div', {'class': 'text show-more__control'})
        review_data = 'NA' if review_data is None else review_data.text

        # get author
        author = review.find('span', {'class': 'display-name-link'})
        author = 'NA' if author is None else author.text

        # get date
        date = review.find('span', {'class': 'review-date'})
        date = 'NA' if date is None else date.text
        date = month_changer(date)

        # users the found it useful
        positive_users = review.find('div', {'class': 'actions text-muted'})
        positive_users = 0 if positive_users is None else int(positive_users.text.split(' ')[20])

        # all users that looked into this review
        all_users = review.find('div', {'class': 'actions text-muted'})
        all_users = 0 if all_users is None else int(all_users.text.split(' ')[23])

        # get percentage of usefulness with respect to all_users
        try:
            percentage_of_usefulness = round(positive_users / all_users * 100, 2)
        except ZeroDivisionError:  # to avoid crash --> 0 if no users have checked the review
            percentage_of_usefulness = 0

        row_df = [film_, year_, author, date, rating, title, review_data, percentage_of_usefulness]

        print('.')

        imdb_df = pd.concat([pd.DataFrame([row_df], columns=imdb_df.columns), imdb_df], ignore_index=True)

    imdb_df.to_sql('disney', conn, if_exists='append', index=False)

#get absolute path (for now)
path = r'C:\Users\Mario\Desktop\Tor Vergata Data Science\Data Warehousing\disney_exam\disney3.db'

#connect to database
conn = sqlite3.connect(path)

#create database if it does not exist already ONLY NEEDS TO BE RUN ONCE
create_db(path = path, conn = conn)

for film, year in zip(film_names , film_years):
    start = time.time()
    # get hml with fully loaded pages and opened warnings sections
    html = get_review_page(film, year)
    # parse info, save it to db, close conn
    beauty_parser(html_page=html, film_= film, year_= year, conn=conn)
    elapsed_time = time.time() - start
    print('It took {} seconds to retrieve all reviews from the film: {} {}'.format(elapsed_time, film, year))

conn.close()






start = time.time()
# get hml with fully loaded pages and opened warnings sections
html = get_review_page('The Sword in the Stone', 1963)
# parse info, save it to db, close conn
beauty_parser(html_page=html, film_='The Sword in the Stone', year_=1950, conn=conn)
elapsed_time = time.time() - start
print('It took {} seconds to retrieve all reviews from the film: {} {}'.format(elapsed_time, 'The Sword in the Stone', 1950))