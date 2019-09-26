import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from util import myhash, get_from_goodreads, get_book_img
from flask import jsonify
import time

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # validate of input
        if not username or not password:
            return render_template("login.html", error="Please fill in username and password.")

        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", 
            {"username": username, "password": myhash(password)})

        if not user.first():
            return render_template("login.html", error="Wrong account or password")
        
        else:
            session["user"] = username
            return redirect("/homepage/1")

    else:
        if session.get("user") is None:
            return render_template("login.html")
        else:
            return redirect("/homepage/1")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        
        # validate of input
        if not username or not password or not confirm:
            return render_template("register.html", error="Please fill in username and password.")

        if password != confirm:
            return render_template("register.html", error="Those passwords didn't match. Try again.")

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        if not user.first():
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
                {"username": username, "password": myhash(password)})
            db.commit()
            return render_template("successful_register.html")
        else:
            return render_template("register.html", error="That username is taken. Try another.")

    else:
        return render_template("register.html", error="")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect("/")

@app.route('/homepage/<page>')
def homepage(page):
    if session.get("user") is None:
        return redirect("/")

    books = db.execute("SELECT isbn, title, author, year, id FROM books LIMIT 9 OFFSET 9 * :page", {"page": str(int(page) - 1)})
    books_list = []

    for row in books:
        row_list = []
        for i in range(5):
            row_list.append(row[i])
        books_list.append(row_list)
    books.close()

    return render_template("homepage.html", books_list=books_list, page=int(page), user=session['user'])

@app.route('/search', methods=["GET", "POST"])
def search():
    if session.get("user") is None:
        return redirect("/")

    query = request.form.get("query")
    if query is None or query == "":
        return render_template("search.html", user=session['user'])
    query = "%" + query + "%"

    books = db.execute("SELECT isbn, title, author, year, id FROM books WHERE isbn LIKE :q OR title LIKE :q OR author LIKE :q OR year LIKE :q LIMIT 30",
                {"q": query})
    
    books_list = []
    for row in books:
        row_list = []
        for i in range(5):
            row_list.append(row[i])
        books_list.append(row_list)
        if len(books_list) == 30:
            break
    books.close()

    return render_template("search_result.html", books_list=books_list, user=session['user'])

@app.route('/top10', methods=["GET", "POST"])
def top10():
    if session.get("user") is None:
        return redirect("/")

    books = db.execute("SELECT books.isbn, books.title, books.author, books.year, books.id, COUNT(book_id) FROM books JOIN reviews ON book_id = books.id \
                        GROUP BY books.isbn, books.title, books.author, books.year, books.id ORDER BY COUNT(book_id) DESC LIMIT 10")
    
    books_list = []
    for row in books:
        row_list = []
        for i in range(6):
            row_list.append(row[i])
        books_list.append(row_list)
        if len(books_list) == 30:
            break
    books.close()

    return render_template("top10.html", books_list=books_list, user=session['user'])

@app.route("/book/<error>/<id>", methods=["GET", "POST"])
def book(id, error = None):
    if session.get("user") is None:
        return redirect("/")
    
    try:
        if int(id) > 5000 or int(id) <= 0:
            return render_template("search_result.html", books_list=[], user=session['user'])
    except:
        return render_template("search_result.html", books_list=[], user=session['user'])

    if request.method == "GET":
        book_query = db.execute("SELECT isbn, title, author, year, id FROM books WHERE id = :id",
            {"id": id})
        book_info = dict(book_query.first())

        average_rating, reviews_count = get_from_goodreads(book_info['isbn'])
        book_info['average_rating'] = average_rating
        book_info['reviews_count'] = reviews_count
        
        book_info['good_read_search'] = "https://www.goodreads.com/search?q=" + str(book_info['isbn'])
        book_info['img_url'] = get_book_img(book_info['isbn'])

        review_query = db.execute("SELECT reviewer, rating, review_text, review_time FROM reviews where book_id = :id",
            {"user": session["user"], "id": id})
        
        reviews = []
        for review in review_query:
            reviews.append(dict(review))

        if error == "0":
            duplication = "1"
            error = None
        elif error == "2":
            duplication = None
        else:
            duplication = None
            error = None

        return render_template("book.html", book_info=book_info, reviews=reviews, error=error, duplication=duplication, user=session['user'])
    else:
        review_query = db.execute("SELECT reviewer, rating, review_text FROM reviews where reviewer = :user AND book_id = :id",
            {"user": session["user"], "id": id})
        
        if review_query.first() is None:
            rating = request.form.get("rating")
            review_text = request.form.get("review_text")
            if not review_text:
                return redirect("/book/2/" + id)

            review_time = time.asctime( time.localtime(time.time()) )
            db.execute("INSERT INTO reviews (book_id, reviewer, rating, review_text, review_time) VALUES (:id, :user, :rating, :review_text, :review_time)",
                {"id": id, "user": session["user"], "rating": rating, "review_text": review_text, "review_time": review_time})
            db.commit()
            return redirect("/book/1/" + id)
        else:
            return redirect("/book/0/" + id)

@app.route("/api/<isbn>")
def api(isbn):
    if session.get("user") is None:
        return redirect("/")

    book_query = db.execute("SELECT title, author, year, isbn, id FROM books WHERE isbn = :isbn",
        {"isbn": isbn})
    book = book_query.first()
    if book is None:
        return "<h1>404 Not Found</h1>"
    book_info = dict(book)

    review_query = db.execute("SELECT COUNT(*), AVG(rating) FROM reviews where book_id = :id",
            {"id": book_info['id']})
    book_info.pop('id')

    review = review_query.first()
    book_info['review_count'] = review[0]
    try:
        book_info['average_score'] = float(review[1])
    except:
        book_info['average_score'] = None

    return jsonify(book_info)
