from flask import Flask, render_template, request, redirect, session
import requests
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

WISHLIST_FILE = "wishlist.json"

# -----------------------
# LOAD & SAVE
# -----------------------
def load_books():
    if not os.path.exists(WISHLIST_FILE):
        return []
    with open(WISHLIST_FILE, "r") as f:
        return json.load(f)

def save_books(books):
    with open(WISHLIST_FILE, "w") as f:
        json.dump(books, f, indent=4)

# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    books = load_books()
    filter_status = request.args.get("filter")

    if filter_status:
        books = [b for b in books if b["status"] == filter_status]

    return render_template("home.html", books=books)

# -----------------------
# SEARCH (Google Books)
# -----------------------
@app.route("/search")
def search():
    query = request.args.get("query")

    if not query:
        return redirect("/")

    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    results = []

    if "items" in data:
        for item in data["items"][:5]:
            info = item["volumeInfo"]

            results.append({
                "title": info.get("title", "N/A"),
                "author": ", ".join(info.get("authors", ["Unknown"])),
                "genre": ", ".join(info.get("categories", ["N/A"]))
            })

    books = load_books()
    return render_template("home.html", books=books, results=results)

# -----------------------
# ADD BOOK (MANUAL OR SEARCH)
# -----------------------
@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    priority = request.form.get("priority")
    status = request.form.get("status")

    if not title:
        return redirect("/")

    books = load_books()

    books.append({
        "title": title,
        "author": author,
        "genre": genre,
        "priority": int(priority),
        "status": status
    })

    save_books(books)

    return redirect("/")

# -----------------------
# REMOVE BOOK
# -----------------------
@app.route("/remove", methods=["POST"])
def remove_book():
    title = request.form.get("title")

    books = load_books()
    books = [b for b in books if b["title"] != title]

    save_books(books)

    return redirect("/")

# -----------------------
# UPDATE BOOK
# -----------------------
@app.route("/update", methods=["POST"])
def update_book():
    title = request.form.get("title")

    books = load_books()

    for book in books:
        if book["title"] == title:
            book["author"] = request.form.get("author")
            book["genre"] = request.form.get("genre")
            book["priority"] = int(request.form.get("priority"))
            book["status"] = request.form.get("status")

    save_books(books)

    return redirect("/")

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
