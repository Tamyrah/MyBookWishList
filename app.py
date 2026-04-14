import os
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# =========================
# DATABASE CONNECTION
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
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
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")  # <-- your Google API key here (Render)

# =========================
# HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title")

        # Prevent duplicates
        cur.execute("SELECT * FROM books WHERE title = %s", (title,))
        existing = cur.fetchone()

        if not existing:
            cur.execute("""
                INSERT INTO books (title, author, genre, priority, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                title,
                request.form.get("author"),
                request.form.get("genre"),
                request.form.get("priority"),
                request.form.get("status")
            ))
            conn.commit()

        return redirect(url_for("home"))

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    return render_template("home.html", wishlist=books)

# =========================
# SEARCH
# =========================
@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = []

    if query:
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}&maxResults=10"
            response = requests.get(url)

            data = response.json()

            for item in data.get("items", []):
                info = item.get("volumeInfo", {})
                results.append({
                    "title": info.get("title", "Unknown"),
                    "author": ", ".join(info.get("authors", ["Unknown"])),
                    "genre": ", ".join(info.get("categories", ["Unknown"]))
                })

        except Exception as e:
            print("ERROR:", e)

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    return render_template("home.html", wishlist=books, search_results=results, query=query)

# =========================
# REMOVE
# =========================
@app.route("/remove", methods=["POST"])
def remove_book():
    title = request.form.get("title")
    cur.execute("DELETE FROM books WHERE title = %s", (title,))
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
        SET title=%s, author=%s, genre=%s, priority=%s, status=%s
        WHERE title=%s
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
