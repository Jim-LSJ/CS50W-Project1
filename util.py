import hashlib
import requests
from bs4 import BeautifulSoup

def myhash(plaintext):
    m = hashlib.sha256()
    m.update(plaintext.encode("utf-8"))
    h = m.hexdigest()
    return h

def get_from_goodreads(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KQQkXflL5QHzU0ReKHopwQ", "isbns": isbn})
    books = res.json()['books']
    average_rating = books[0]['average_rating']
    reviews_count = books[0]['reviews_count']
    if average_rating is None:
        average_rating = "Not found"
    if reviews_count is None:
        reviews_count = "Not found"

    return average_rating, reviews_count

def get_book_img(isbn):
    r = requests.get("https://www.goodreads.com/search?q=" + isbn)
    soup = BeautifulSoup(r.text, "html.parser")
    img_url = soup.find('img', id='coverImage').get('src')
    return img_url