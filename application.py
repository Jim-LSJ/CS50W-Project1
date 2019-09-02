import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from util import myhash, get_from_goodreads
from flask import jsonify

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

    books = db.execute("SELECT isbn, title, author, year, id FROM books LIMIT 9 OFFSET 9 * :page", {"page": str((int(page) - 1))})
    books_list = []

    for row in books:
        row_list = []
        for i in range(5):
            row_list.append(row[i])
        books_list.append(row_list)
    books.close()

    return render_template("homepage.html", books_list=books_list, page=int(page), user=session['user'][0])

@app.route('/search', methods=["GET", "POST"])
def search():
    if session.get("user") is None:
        return redirect("/")

    query = request.form.get("query")
    if query is None or query == "":
        return render_template("search.html", user=session['user'][0])
    query = "%" + query + "%"

    books = db.execute("SELECT isbn, title, author, year, id FROM books WHERE isbn LIKE :q OR title LIKE :q OR author LIKE :q OR year LIKE :q",
                {"q": query})
    
    books_list = []
    for row in books:
        row_list = []
        for i in range(5):
            row_list.append(row[i])
        books_list.append(row_list)
    books.close()

    return render_template("search_result.html", books_list=books_list, user=session['user'][0])

@app.route("/book/<error>/<id>", methods=["GET", "POST"])
def book(id, error = None):
    if session.get("user") is None:
        return redirect("/")

    if request.method == "GET":
        book_query = db.execute("SELECT isbn, title, author, year, id FROM books WHERE id = :id",
            {"id": id})
        book_info = dict(book_query.first())

        avg_rating, work_ratings_count = get_from_goodreads(book_info['isbn'])
        book_info['avg_rating'] = avg_rating
        book_info['work_ratings_count'] = work_ratings_count

        review_query = db.execute("SELECT reviewer, rating, review_text FROM reviews where book_id = :id",
            {"user": session["user"], "id": id})
        
        reviews = []
        for review in review_query:
            reviews.append(dict(review))

        if error != "0":
            error = None

        return render_template("book.html", book_info=book_info, reviews=reviews, error=error, user=session['user'][0])
    else:
        review_query = db.execute("SELECT reviewer, rating, review_text FROM reviews where reviewer = :user AND book_id = :id",
            {"user": session["user"], "id": id})
        
        if review_query.first() is None:
            rating = request.form.get("rating")
            review_text = request.form.get("review_text")

            db.execute("INSERT INTO reviews (book_id, reviewer, rating, review_text) VALUES (:id, :user, :rating, :review_text)",
                {"id": id, "user": session["user"], "rating": rating, "review_text": review_text})
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



