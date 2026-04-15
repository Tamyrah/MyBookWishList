from flask import Flask, render_template, request, redirect
import requests
import os
import json

app = Flask(__name__)

DATA_FILE = "wishlist.json"

# ---------- LOAD / SAVE ----------
def load_books():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f, indent=4)

# ---------- HOME ----------
@app.route("/")
def home():
    books = load_books()
    filter_status = request.args.get("filter")

    if filter_status:
        books = [b for b in books if b["status"] == filter_status]

    return render_template("home.html", books=books)

# ---------- SEARCH ----------
@app.route("/search")
def search():
    query = request.args.get("q")

    if not query:
        return redirect("/")

    API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"
    response = requests.get(url).json()

    results = []

    if "items" in response:
        for item in response["items"][:5]:
            info = item["volumeInfo"]

            results.append({
                "title": info.get("title", "Unknown"),
                "author": ", ".join(info.get("authors", ["Unknown"])),
                "genre": ", ".join(info.get("categories", ["Unknown"]))
            })

    return render_template("home.html", books=load_books(), results=results)

# ---------- ADD ----------
@app.route("/add", methods=["POST"])
def add():
    books = load_books()

    new_book = {
        "id": len(books) + 1,
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": request.form.get("priority"),
        "status": request.form.get("status")
    }

    books.append(new_book)
    save_books(books)

    return redirect("/")

# ---------- ADD FROM SEARCH ----------
@app.route("/add_from_search", methods=["POST"])
def add_from_search():
    books = load_books()

    new_book = {
        "id": len(books) + 1,
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": request.form.get("priority"),
        "status": request.form.get("status")
    }

    books.append(new_book)
    save_books(books)

    return redirect("/")

# ---------- UPDATE ----------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    books = load_books()

    for book in books:
        if book["id"] == id:
            book["priority"] = request.form.get("priority")
            book["status"] = request.form.get("status")

    save_books(books)
    return redirect("/")

# ---------- DELETE ----------
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    books = load_books()
    books = [b for b in books if b["id"] != id]
    save_books(books)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
