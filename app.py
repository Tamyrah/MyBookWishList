from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
import requests

app = Flask(__name__)

# =========================
# DATABASE CONNECTION FIXED
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix for Render postgres:// issue
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT,
            author TEXT,
            genre TEXT,
            priority INTEGER,
            status TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# =========================
# HOME PAGE
# =========================
@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books ORDER BY id DESC;")
    books = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("home.html", books=books)

# =========================
# ADD BOOK (MANUAL)
# =========================
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    priority = request.form.get('priority')
    status = request.form.get('status')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books (title, author, genre, priority, status)
        VALUES (%s, %s, %s, %s, %s);
    """, (title, author, genre, priority, status))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('home'))

# =========================
# REMOVE BOOK
# =========================
@app.route('/remove/<int:book_id>', methods=['POST'])
def remove_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('home'))

# =========================
# UPDATE BOOK
# =========================
@app.route('/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    priority = request.form.get('priority')
    status = request.form.get('status')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE books
        SET title=%s, author=%s, genre=%s, priority=%s, status=%s
        WHERE id=%s;
    """, (title, author, genre, priority, status, book_id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('home'))

# =========================
# SEARCH (GOOGLE BOOKS API)
# =========================
@app.route('/search')
def search():
    query = request.args.get('q')
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")

    results = []

    if query and api_key:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if "items" in data:
            for item in data["items"]:
                volume = item["volumeInfo"]

                results.append({
                    "title": volume.get("title", "No title"),
                    "author": ", ".join(volume.get("authors", ["Unknown"])),
                    "genre": ", ".join(volume.get("categories", ["Unknown"]))
                })

    # Also load existing books
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books ORDER BY id DESC;")
    books = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("home.html", books=books, search_results=results)

# =========================
# ADD BOOK FROM SEARCH
# =========================
@app.route('/add_from_search', methods=['POST'])
def add_from_search():
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    priority = request.form.get('priority')
    status = request.form.get('status')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books (title, author, genre, priority, status)
        VALUES (%s, %s, %s, %s, %s);
    """, (title, author, genre, priority, status))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('home'))

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
