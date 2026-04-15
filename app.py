from flask import Flask, render_template, request, redirect
import requests
import os

app = Flask(__name__)

wishlist = []

# HOME + FILTER
@app.route("/", methods=["GET"])
def home():
    filter_status = request.args.get("filter")

    if filter_status and filter_status != "All":
        filtered_list = [book for book in wishlist if book["status"] == filter_status]
    else:
        filtered_list = wishlist

    return render_template("home.html", wishlist=filtered_list)

# ADD BOOK
@app.route("/add", methods=["POST"])
def add_book():
    new_book = {
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": request.form.get("priority"),
        "status": request.form.get("status")
    }

    wishlist.append(new_book)
    return redirect("/")

# REMOVE
@app.route("/remove", methods=["POST"])
def remove_book():
    global wishlist
    title = request.form.get("title")

    wishlist = [book for book in wishlist if book["title"] != title]
    return redirect("/")

# EDIT
@app.route("/edit", methods=["POST"])
def edit_book():
    original_title = request.form.get("original_title")

    for book in wishlist:
        if book["title"] == original_title:
            book["title"] = request.form.get("title")
            book["author"] = request.form.get("author")
            book["genre"] = request.form.get("genre")
            book["priority"] = request.form.get("priority")
            book["status"] = request.form.get("status")

    return redirect("/")

# SEARCH
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")

    if not query:
        return redirect("/")

    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

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

    return render_template("home.html", wishlist=wishlist, search_results=results)

if __name__ == "__main__":
    app.run(debug=True)
