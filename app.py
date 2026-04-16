from flask import Flask, render_template, request, redirect
import requests
import os
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    user_key = request.args.get("user")

    if not user_key:
        return render_template("enter.html")

    books = supabase.table("books").select("*").eq("user_id", user_key).execute().data

    return render_template("home.html", books=books, results=[], user_key=user_key)

# -----------------------
# ADD BOOK
# -----------------------
@app.route("/add", methods=["POST"])
def add_book():
    user_key = request.form.get("user_key")

    supabase.table("books").insert({
        "user_id": user_key,
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status")
    }).execute()

    return redirect(f"/?user={user_key}")

# -----------------------
# REMOVE BOOK
# -----------------------
@app.route("/remove", methods=["POST"])
def remove_book():
    user_key = request.form.get("user_key")
    book_id = request.form.get("book_id")

    supabase.table("books").delete().eq("id", book_id).execute()

    return redirect(f"/?user={user_key}")

# -----------------------
# UPDATE BOOK
# -----------------------
@app.route("/update", methods=["POST"])
def update_book():
    user_key = request.form.get("user_key")
    book_id = request.form.get("book_id")

    supabase.table("books").update({
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status")
    }).eq("id", book_id).execute()

    return redirect(f"/?user={user_key}")

# -----------------------
# SEARCH
# -----------------------
@app.route("/search")
def search():
    user_key = request.args.get("user")
    query = request.args.get("query")

    books = supabase.table("books").select("*").eq("user_id", user_key).execute().data

    results = []

    if query and query.strip() != "":
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url).json()

        if "items" in response:
            for item in response["items"][:5]:
                info = item["volumeInfo"]
                results.append({
                    "title": info.get("title", ""),
                    "author": ", ".join(info.get("authors", ["Unknown"])),
                    "genre": ", ".join(info.get("categories", [""]))
                })

    return render_template("home.html", books=books, results=results, user_key=user_key)

if __name__ == "__main__":
    app.run(debug=True)
