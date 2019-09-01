import hashlib
import requests

def myhash(plaintext):
    m = hashlib.sha256()
    m.update(plaintext.encode("utf-8"))
    h = m.hexdigest()
    return h

def get_from_goodreads(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KQQkXflL5QHzU0ReKHopwQ", "isbns": isbn})
    books = res.json()['books']
    average_rating = books[0]['average_rating']
    review_count = books[0]['reviews_count']
    if average_rating is None:
        average_rating = "Not found"
    if review_count is None:
        review_count = "Not found"

    return average_rating, review_count