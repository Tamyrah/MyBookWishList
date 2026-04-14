import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

wishlist = []

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# =========================
# HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    global wishlist

    if request.method == "POST":
        new_book = {
            "title": request.form.get("title"),
            "author": request.form.get("author"),
            "genre": request.form.get("genre"),
            "priority": request.form.get("priority") or "3",
            "status": request.form.get("status") or "Want to Read"
        }

        if not any(book["title"] == new_book["title"] for book in wishlist):
            wishlist.append(new_book)

        return redirect(url_for("home"))

    return render_template("home.html", wishlist=wishlist, search_results=None, query="")

# =========================
# SEARCH
# =========================
@app.route("/search", methods=["GET"])
def search():
    global wishlist

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

    return render_template("home.html", wishlist=wishlist, search_results=results, query=query)

# =========================
# ADD FROM SEARCH
# =========================
@app.route("/add_from_search", methods=["POST"])
def add_from_search():
    global wishlist

    new_book = {
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": request.form.get("priority") or "3",
        "status": request.form.get("status") or "Want to Read"
    }

    if not any(book["title"] == new_book["title"] for book in wishlist):
        wishlist.append(new_book)

    return redirect(url_for("home"))

# =========================
# REMOVE
# =========================
@app.route("/remove", methods=["POST"])
def remove_book():
    global wishlist
    title = request.form.get("title")
    wishlist = [book for book in wishlist if book["title"] != title]
    return redirect(url_for("home"))

# =========================
# EDIT (THIS WAS MISSING IN FLOW)
# =========================
@app.route("/edit", methods=["POST"])
def edit_book():
    global wishlist

    original_title = request.form.get("original_title")

    for book in wishlist:
        if book["title"] == original_title:
            book["title"] = request.form.get("title")
            book["author"] = request.form.get("author")
            book["genre"] = request.form.get("genre")
            book["priority"] = request.form.get("priority")
            book["status"] = request.form.get("status")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
