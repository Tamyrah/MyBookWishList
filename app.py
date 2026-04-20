from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

# TEMP in-memory storage (we will reconnect database later)
books = []

# 🔥 GOOGLE BOOKS SEARCH
def search_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    data = response.json()

    results = []

    if "items" in data:
        for item in data["items"][:5]:
            info = item["volumeInfo"]

            results.append({
                "title": info.get("title", "No Title"),
                "author": ", ".join(info.get("authors", ["Unknown"])),
                "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                "link": info.get("infoLink", "#")
            })

    return results

# HOME
@app.route("/")
def home():
    return render_template("home.html", results=[], books=books)

# 🔍 SEARCH ROUTE
@app.route("/search")
def search():
    query = request.args.get("query")

    if not query:
        return render_template("home.html", results=[], books=books)

    results = search_books(query)

    return render_template("home.html", results=results, books=books)

# ➕ ADD BOOK
@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    priority = request.form.get("priority")
    status = request.form.get("status")

    books.insert(0, {
        "title": title,
        "author": author,
        "genre": genre,
        "priority": priority,
        "status": status
    })

    return redirect("/")

# ❌ REMOVE BOOK
@app.route("/remove_book", methods=["POST"])
def remove_book():
    title = request.form.get("title")

    global books
    books = [b for b in books if b["title"] != title]

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
