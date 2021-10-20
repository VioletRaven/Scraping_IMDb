from selenium import webdriver
from bs4 import BeautifulSoup
import time
import datetime
import calendar
import sqlite3

# Selenium
'''

La funzione `start_driver()` crea un driver per il browser Chrome.
Assegna una directory (che deve essere precedentemente creata per il salvataggio dei cookie 
e delle informazioni utente per eventuali login a pagine web
Infine imposta il path al *chromedriver* che può essere assoluto o relativo.

'''
fifties = ['Peter pan', 'Alice in wonderland', 'Cinderella']
sixties = []
seventies = []
eighties = []
nineties = []
twothousand = []
twothousandten = []

#films = {'fifties' : ['cenerentola', 'shit', 'yoyo'], 'sixties' : ['lilly', 'ciao', 'sex']}

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
    for warning in warnings:
        print("click", end=",\n")
        warning.click()
        time.sleep(1)

    html = driver.page_source
    driver.quit()

    return html

#function needed for good formatting when saving as datetime object
def month_changer(date):
    month = date.split(' ')[1]
    month_num = datetime.datetime.strptime(month, '%B').month
    month_name = calendar.month_abbr[month_num]
    return date.split(' ')[0] + ' ' + month_name + ' ' + date.split(' ')[2]

def create_db(path):
    conn = sqlite3.connect(path)

    conn.execute("""
    CREATE TABLE disney (
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
    conn.close()



def save_to_db(film_name, film_year, author_name, review_date, score, title_name, review_text, POU):

    conn.execute("""
    INSERT INTO disney (
                           film_name,
                           film_year,
                           author_name,
                           review_date,
                           score,
                           title_name,
                           review_text,
                           POU
                       )
                       VALUES ( 
                           "%s",
                           "%d",
                           "%s",
                           "%s",
                           "%f",
                           "%s",
                           "%s",
                           "%f"
                        );
    """ % (film_name, film_year, author_name, review_date, score, title_name, review_text, POU))
    conn.commit()

def beauty_parser(html_page, film_, year_):

    # loop to parse through reviews and populate dataset

    # parsing html page
    soup = BeautifulSoup(html_page, "html.parser")
    reviews = soup.find_all("div", {"class": "lister-item"})

    for review in reviews:
        # get rating
        rating = review.find("span", {"class": "rating-other-user-rating"})
        rating = None if rating is None else int(rating.text.strip().split("/")[0])

        # get title
        title = review.find("a", {"class": "title"})
        title = None if title is None else title.text.strip()

        # get review

        review_data = review.find('div', {'class': 'text show-more__control'})
        review_data = None if review_data is None else review_data.text

        # get author
        author = review.find('span', {'class': 'display-name-link'})
        author = None if author is None else author.text

        # get date
        date = review.find('span', {'class': 'review-date'})
        date = None if date is None else date.text
        date = month_changer(date)

        # users the found it useful
        positive_users = review.find('div', {'class': 'actions text-muted'})
        positive_users = None if positive_users is None else int(positive_users.text.split(' ')[20])

        # all users that looked into this review
        all_users = review.find('div', {'class': 'actions text-muted'})
        all_users = None if all_users is None else int(all_users.text.split(' ')[23])

        # get percentage of usefulness with respect to all_users
        try:
            percentage_of_usefulness = round(positive_users / all_users * 100, 2)
        except ZeroDivisionError:  # to avoid crash --> 0 if no users have checked the review
            percentage_of_usefulness = 0



        print(film_, year_, author, date, rating, title, review_data, percentage_of_usefulness)
        save_to_db(film_name = film_, film_year = year_,
                    author_name = author, review_date= date,
                    score = rating, title_name = title,
                    review_text = review_data, POU = percentage_of_usefulness)


path = r'C:\Users\Mario\Desktop\Tor Vergata Data Science\Data Warehousing\disney_exam\disney3.db'

create_db(path)
# creiamo un database vuoto
conn = sqlite3.connect(path)

html = get_review_page('peter pan', 1953)
beauty_parser(html_page = html, film_ = 'peter pan', year_ = 1953)
conn.close()






soup = BeautifulSoup(html, "html.parser")
reviews = soup.find_all("div", {"class": "lister-item"})

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

    print(author,'\n', date,'\n', rating,'\n', title,'\n', review_data,'\n', percentage_of_usefulness,'\n')


#DEBUGGING HERE

    conn.execute("""
    INSERT INTO disney (
                           film_name,
                           film_year,
                           author_name,
                           review_date,
                           score,
                           title_name,
                           review_text,
                           POU
                       )
                       VALUES ( 
                           "%s",
                           "%d",
                           "%s",
                           "%s",
                           "%f",
                           "%s",
                           "%s",
                           "%f"
                        );
    """ % ('peter pan', 1953, str(author),  str(date), float(rating),  str(title),  str(review_data), float(percentage_of_usefulness)))
    conn.commit()





# IF I RUN IT MANUALLY IT WORKS BUT IT DOESN'T IN A FOR LOOP WTFFFFF
conn.execute("""
    INSERT INTO disney (
                           film_name,
                           film_year,
                           author_name,
                           review_date,
                           score,
                           title_name,
                           review_text,
                           POU
                       )
                       VALUES ( 
                           "%s",
                           "%d",
                           "%s",
                           "%s",
                           "%f",
                           "%s",
                           "%s",
                           "%f"
                        );
    """ % ('peter pan', 1953, 'martin', '14 Jul 2013 ', 9, 'yogurt ', 'yes', 67.92))
conn.commit()

conn.execute("""
  INSERT INTO disney (
                         film_name,
                         film_year,
                         author_name,
                         review_date,
                         score,
                         title_name,
                         review_text,
                         POU
                     )
                     VALUES ( 
                         "%s",
                         "%d",
                         "%s",
                         "%s",
                         "%d",
                         "%s",
                         "%s",
                         "%d"
                      );
  """ % ('peter pan', 1953, 's', 'yo', 5, 'tu', 'forget', 2))
conn.commit()



# different try

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="andrea",
  database="disney"
)

mycursor = mydb.cursor()

sql = "INSERT INTO dysney (name, address) VALUES (%s, %s)"


values = []
val = ("John", "Highway 21")
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")






years = [1950,1932,1956]
films = ['bella ciao', 'che cazzo ti guardi', 'monossido di carbonio']





text = 'peter pan'
driver = start_chrome_driver()
driver.get("https://www.imdb.com/")
search = driver.find_element_by_id("suggestion-search")
for letter in text:
    search.send_keys(letter)
    time.sleep(.1)
button = driver.find_element_by_id("suggestion-search-button")
button.click()


diff_movies = driver.find_elements_by_class_name('result_text')
movie = 0
year = '1953'
for n, i in enumerate(diff_movies):
    if year in i.text:
        movie += n

button = diff_movies[movie]

#get href button by xpath and enter movie page
button = button.find_element_by_xpath('//*[@id="main"]/div/div[2]/table/tbody/tr[3]/td[2]/a')
button.click()

#enter reviews
new_button = driver.find_element_by_xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/ul/li[1]/a')
new_button.click()

more = driver.find_element_by_id("load-more-trigger")
while more.is_displayed():
    print('loading...')
    more.click()
    time.sleep(2)
    more = driver.find_element_by_id("load-more-trigger")

warnings = driver.find_elements_by_class_name("spoiler-warning__control")
for warning in warnings:
    print("click", end=",\n")
    warning.click()
    time.sleep(1)

# parsing html page now

soup = BeautifulSoup(html, "html.parser")
reviews = soup.find_all("div", {"class": "lister-item"})
ratingdata = reviews[0].find("span", {"class": "rating-other-user-rating"})
#int(ratingdata.text.strip().split("/")[0]) # --> get score
ratingvalue = None if ratingdata is None else int(ratingdata.text.strip().split("/")[0])
titledata = reviews[0].find("a", {"class": "title"})
titledata.text.strip()
titlevalue = None if titledata is None else titledata.text.strip()
review_data = reviews[0].find('div', {'class':'text show-more__control'})
review_data = None if review_data is None else review_data.text

date = reviews[0].find('span', {'class':'review-date'})
date = None if date is None else date.text
date = month_changer(date)

#was it useful?

positive_users = reviews[0].find('div', {'class':'actions text-muted'})
positive_users  = None if positive_users  is None else positive_users .text.split(' ')[20]

all_users = reviews[0].find('div', {'class':'actions text-muted'})
all_users = None if all_users  is None else all_users .text.split(' ')[23]




#conn = requests.get(url)
#html = conn.text


for year, film in zip(years, films):
    html = get_review_page(film, year)
    beauty_parser(html_page = html)
    salva_su_db()


