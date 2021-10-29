import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

path = r'C:\Users\Mario\Desktop\Tor Vergata Data Science\Data Warehousing\disney_exam\disney3.db'
def create_db(path):
    conn = sqlite3.connect(path)

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
    conn.close()

#run this to create table in sql
create_db(path)
df.to_sql('disney', conn, if_exists='append', index=False)

# parsing html page now

soup = BeautifulSoup(html, "html.parser")
reviews = soup.find_all("div", {"class": "lister-item"})


df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})

imdb_df = pd.DataFrame(columns = ['film_name', 'film_year', 'author_name', 'review_date',
                                  'score', 'title_name', 'review_text', 'POU'])


row_df = ['ciao', 'fo', 'ss', 5, 'dd', '112', 190.2, '7ld']

for i in range(100):
    imdb_df = pd.DataFrame(columns=['film_name', 'film_year', 'author_name', 'review_date',
                                    'score', 'title_name', 'review_text', 'POU'])




film_ = 'peter pan'
year_ = 1953
imdb_df = pd.DataFrame(columns = ['film_name', 'film_year', 'author_name', 'review_date',
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

    #print(author,'\n', date,'\n', rating,'\n', title,'\n', review_data,'\n', percentage_of_usefulness,'\n')

    imdb_df = pd.concat([pd.DataFrame([row_df], columns=imdb_df.columns), imdb_df], ignore_index=True)

imdb_df.to_sql('disney', conn, if_exists = 'append', index=False)


#engine.execute("SELECT * FROM users").fetchall()





















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














df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})
df.to_sql('users', con=engine)
#engine.execute("SELECT * FROM users").fetchall()












# populating a dataframe with a for loop and pandas
rows = [[i, k, z, ...] for i, k, z, ... in [[...]]]
df = pd.DataFrame(rows, columns=["A", "B"])