from flask import Flask, render_template, request, redirect
from supabase import create_client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def enter():
    return render_template("enter.html")

@app.route("/home")
def home():
    user_key = request.args.get("user")
    books = supabase.table("books").select("*").eq("user_id", user_key).execute().data
    return render_template("home.html", books=books, results=[], user_key=user_key)

@app.route("/add", methods=["POST"])
def add():
    user_key = request.form.get("user")
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    priority = request.form.get("priority")
    status = request.form.get("status")

    supabase.table("books").insert({
        "user_id": user_key,
        "title": title,
        "author": author,
        "genre": genre,
        "priority": int(priority),
        "status": status
    }).execute()

    return redirect(f"/home?user={user_key}")

@app.route("/update", methods=["POST"])
def update():
    user_key = request.form.get("user")
    book_id = request.form.get("id")

    supabase.table("books").update({
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status")
    }).eq("id", book_id).execute()

    return redirect(f"/home?user={user_key}")

@app.route("/remove", methods=["POST"])
def remove():
    user_key = request.form.get("user")
    book_id = request.form.get("id")

    supabase.table("books").delete().eq("id", book_id).execute()

    return redirect(f"/home?user={user_key}")

@app.route("/search")
def search():
    user_key = request.args.get("user")
    query = request.args.get("query")

    import requests
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url).json()

    results = []
    for item in response.get("items", [])[:5]:
        volume = item.get("volumeInfo", {})
        results.append({
            "title": volume.get("title"),
            "author": ", ".join(volume.get("authors", ["Unknown"])),
            "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
            "description": volume.get("description", "")[:200]
        })

    books = supabase.table("books").select("*").eq("user_id", user_key).execute().data

    return render_template("home.html", books=books, results=results, user_key=user_key)

if __name__ == "__main__":
    app.run(debug=True)
