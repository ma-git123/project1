import os, json

from flask import Flask, session, render_template, request, url_for, jsonify, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
app.secret_key = "super secret key"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
#engine = create_engine("postgres://vieenkduytljyx:bd1ceaf70ff3f1968c5e1152fa907bbc3cbd58f16ef7aed316566d9d2935c36e@ec2-34-193-117-204.compute-1.amazonaws.com:5432/ddck39i38rj44")
db = scoped_session(sessionmaker(bind=engine))

# Goodreads Key
goodreads_key = '1ck8y5hWnaG0yJZ2drQj0A'


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST": 
        username = request.form['username']
        password = request.form['password']        
        error = None
        if not request.form.get("username"):
            return render_template('index.html', danger ='username is required')
        elif not request.form.get("password"):
            return render_template('index.html', danger='password is required')
        user = db.execute("SELECT username FROM users WHERE username = :username;", {"username": username}).fetchone()
        pas = db.execute("SELECT password FROM users WHERE password = :password;", {"password": password}).fetchone()
        if user is None:
            return render_template('index.html', danger='Incorrect username')
        elif pas is None:
            return render_template("index.html", danger="Incorrect password")
        else:
            session.clear()
            session["logged_in"] = True
            session['user_id'] = user[0]
            session["username"] = username

            books = db.execute("SELECT * FROM books").fetchall()
            return render_template("books.html", books=books, username=username, success = True)

    if request.method == "GET": 
        if session.get('username') is None:
            return render_template("index.html")
        else:
            books = db.execute("SELECT * FROM books").fetchall()
            return render_template("books.html", books=books)           

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username=request.form['username']
        password=request.form['password']
        #error=""
        if not request.form.get("username"):
            return render_template("register.html", danger = "username is required")
        uniqueUsername = db.execute("SELECT * FROM users WHERE username = :username", {"username":request.form.get("username")}).fetchone()
        if uniqueUsername:
            return render_template("register.html", danger = "username is not valid")
        elif not request.form.get("password"): 
            return render_template("register.html", danger = "password is required")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
        return render_template("index.html", success = "You have successfully registered. Log in to join")
    if request.method == "GET":
        return render_template("register.html")    


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/books", methods=['POST', 'GET'])
def books():

    if request.method == "POST":
        if session.get('username') is None:
            return render_template("index.html", danger = "You should login")
        else:
            searched_book = request.form['book'].lower()

            if searched_book:
               searched_book = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn or lower(title) LIKE :title or lower(author) LIKE :author",{'isbn':"%" + searched_book + "%",'title':"%" + searched_book + "%", 'author':"%" + searched_book+"%"})
               books = searched_book.fetchall()

            if not request.form.get("book"):
                books = db.execute("SELECT * FROM books").fetchall()
                return render_template("books.html", books=books, message="Please insert your search key")

            if books:
                return render_template("results.html", books=books)
                
            else:
                books = db.execute("SELECT * FROM books").fetchall()
                return render_template("books.html", books=books, message="book not found")  

    if request.method == "GET":
        if session.get('username') is None:
            return render_template("index.html", danger = "You should login")
        else:
            books = db.execute("SELECT * FROM books").fetchall()
            return render_template("books.html", books=books)
          

@app.route("/books/<string:book_id>", methods=['POST', 'GET'])
def details(book_id):

    if request.method == "POST":
        if session.get('username') is None:
            return render_template("index.html", danger = "You should login")
        else:
            rating = request.form['rating']
            review = request.form['review']
            isbn = request.form['isbn']

            username_review = session.get('username')

            user_review = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": username_review, "isbn": isbn})
            checkuser = user_review.fetchone()

            if checkuser:
                books = db.execute("SELECT * FROM books").fetchall()
                return render_template("books.html",  books=books, message = " You have already submitted a review for this book. You can not write more than one review for one book")
            else:
                db.execute("INSERT INTO reviews (isbn, rating, review, username) VALUES (:isbn, :rating, :review, :username)", {"isbn": isbn, "rating":rating, "review":review, "username":username_review})
                db.commit()
                books = db.execute("SELECT * FROM books").fetchall()
                return render_template("books.html",  books=books, messagesuccess = " You have successfully submitted a review.")
                
            
    if request.method == "GET":
        if session.get('username') is None:
            return render_template("index.html", danger = "You should login")
        else:            
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_id}).fetchone()

            review = db.execute("SELECT username, review, rating FROM reviews WHERE isbn = :isbn", {"isbn": book_id})
            reviews = review.fetchall()

            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key, "isbns": book_id}) 
            data = res.json()
            rating = data['books'][0]['work_ratings_count']
            average = data['books'][0]['average_rating']
            return render_template("details.html", book=book, reviews=reviews, rating=rating, average=average)


@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    if session.get('username') is None:
        return render_template("index.html", danger = "You should login")
    else:
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        review_count = db.execute("SELECT count(review) FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).scalar()
        sum_rating = db.execute("SELECT sum(rating) FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).scalar()
        count_rating = db.execute("SELECT count(rating) FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).scalar()
        average_score = sum_rating / count_rating

        if book is None:
            return jsonify({"error": "Invalid book ISBN"}), 404
        else:
            return jsonify({
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "review_count": review_count,
                "average_score": average_score
                })