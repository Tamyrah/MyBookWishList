import os
import requests
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# =========================
# DATABASE (LOCAL SQLITE)
# =========================
conn = sqlite3.connect("books.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    genre TEXT,
    priority TEXT,
    status TEXT
)
""")
conn.commit()

# =========================
# GOOGLE API KEY
# =========================
GOOGLE_BOOKS_API_KEY = "your Google API key here"

# =========================
# HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title")

        # prevent duplicates
        cur.execute("SELECT * FROM books WHERE title=?", (title,))
        existing = cur.fetchone()

        if not existing:
            cur.execute("""
                INSERT INTO books (title, author, genre, priority, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                title,
                request.form.get("author"),
                request.form.get("genre"),
                request.form.get("priority") or "3",
                request.form.get("status") or "Want to Read"
            ))
            conn.commit()

        return redirect(url_for("home"))

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    return render_template("home.html", wishlist=books, search_results=None, query="")

# =========================
# SEARCH
# =========================
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    results = []

    if query:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10&key={GOOGLE_BOOKS_API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for item in data.get("items", []):
                info = item.get("volumeInfo", {})

                results.append({
                    "title": info.get("title", "Unknown"),
                    "author": ", ".join(info.get("authors", ["Unknown"])),
                    "genre": ", ".join(info.get("categories", ["Unknown"]))
                })

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    return render_template("home.html", wishlist=books, search_results=results, query=query)

# =========================
# ADD FROM SEARCH
# =========================
@app.route("/add_from_search", methods=["POST"])
def add_from_search():
    title = request.form.get("title")

    cur.execute("SELECT * FROM books WHERE title=?", (title,))
    existing = cur.fetchone()

    if not existing:
        cur.execute("""
            INSERT INTO books (title, author, genre, priority, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            title,
            request.form.get("author"),
            request.form.get("genre"),
            request.form.get("priority") or "3",
            request.form.get("status") or "Want to Read"
        ))
        conn.commit()

    return redirect(url_for("home"))

# =========================
# REMOVE
# =========================
@app.route("/remove", methods=["POST"])
def remove_book():
    title = request.form.get("title")
    cur.execute("DELETE FROM books WHERE title=?", (title,))
    conn.commit()
    return redirect(url_for("home"))

# =========================
# EDIT
# =========================
@app.route("/edit", methods=["POST"])
def edit_book():
    original_title = request.form.get("original_title")

    cur.execute("""
        UPDATE books
        SET title=?, author=?, genre=?, priority=?, status=?
        WHERE title=?
    """, (
        request.form.get("title"),
        request.form.get("author"),
        request.form.get("genre"),
        request.form.get("priority"),
        request.form.get("status"),
        original_title
    ))
    conn.commit()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
