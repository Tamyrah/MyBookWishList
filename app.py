from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app, supports_credentials=True)

# TEMP storage (per user token)
books_db = {}

def get_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    return auth_header.split(" ")[1]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/books", methods=["GET"])
def get_books():
    user = get_user()
    if not user:
        return jsonify([])
    return jsonify(books_db.get(user, []))

@app.route("/add-book", methods=["POST"])
def add_book():
    user = get_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    book = {
        "id": str(uuid.uuid4()),
        "title": data.get("title"),
        "author": data.get("author"),
        "genre": data.get("genre"),
        "priority": data.get("priority"),
        "status": data.get("status")
    }

    books_db.setdefault(user, []).append(book)
    return jsonify(book)

@app.route("/remove-book/<book_id>", methods=["DELETE"])
def remove_book(book_id):
    user = get_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    books_db[user] = [
        b for b in books_db.get(user, [])
        if b["id"] != book_id
    ]

    return jsonify({"status": "deleted"})

@app.route("/update-book/<book_id>", methods=["PUT"])
def update_book(book_id):
    user = get_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    for b in books_db.get(user, []):
        if b["id"] == book_id:
            b.update({
                "title": data.get("title"),
                "author": data.get("author"),
                "genre": data.get("genre"),
                "priority": data.get("priority"),
                "status": data.get("status")
            })

    return jsonify({"status": "updated"})

@app.route("/search")
def search():
    query = request.args.get("query", "").lower()

    sample_books = [
        {"title": "Harry Potter and the Chamber of Secrets", "author": "J.K. Rowling"},
        {"title": "The Hate U Give", "author": "Angie Thomas"},
        {"title": "Atomic Habits", "author": "James Clear"},
        {"title": "The Alchemist", "author": "Paulo Coelho"},
        {"title": "Disappearing Acts", "author": "Terry McMillan"}
    ]

    results = [b for b in sample_books if query in b["title"].lower()]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
