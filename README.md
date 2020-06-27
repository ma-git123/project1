# Project 1

Web Programming with Python and JavaScript

## Book Review website

This is a book review website build with Flask and SQLAlchemy database to practice content of lecture 2, lecture 3 and lecture 4.
Users can register and create an account and then log in to use this website using their username and password. Once they log in, they will be able to search for books, leave just one review for individual books, and see the reviews made by other users of the website. in this website a third-party API by Goodreads is used to pull in ratings from Goodreads. Moreover, users will be able to query for book details and book reviews programmatically via the website’s API.

```

## Table of contents

* layout.html Contains a global template which is used for all pages.
* index.html Contains login form and link to registeration page. 
* register.html Contains registeration form and link to login page. 
* books.html  Once a user has logged in, they can search for a book by typing complete or part of the ISBN number of a book, the title of a book, or the author of a book. 
* results.html After performing the search, this results page will be displayed a list of possible matching results, or a message if there were no matches. 
* details.html This page contains details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website. User can also write just one review for the book in this page consisting of a rating on a scale of 1 to 5, as well as a text. Moreover, the average rating and number of ratings the work from Goodreads is displayed for any indivitual book in details page which is provided via a third-party API.
* If users make a GET request to the website’s /api/<isbn> route, where <isbn> is an ISBN number of a book, the website will return a JSON response containing the book’s title, author, publication date, ISBN number, user's review count from this website, and user's average score. If the requested ISBN number isn’t in the database, the website will return a 404 error.

## to run this peoject set DATABASE_URL to heroku url
