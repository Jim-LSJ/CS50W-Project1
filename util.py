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
    
    avg_rating = books[0]['average_rating']
    work_ratings_count = books[0]['work_ratings_count']
    if avg_rating is None:
        avg_rating = "Not found"
    if work_ratings_count is None:
        work_ratings_count = "Not found"

    return avg_rating, work_ratings_count