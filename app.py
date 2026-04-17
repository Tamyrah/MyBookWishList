from flask import Flask, render_template, request, redirect
from supabase import create_client
import os
import requests

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
    filter_status = request.args.get("filter")

    query = supabase.table("books").select("*").eq("user_id", user_key)

    if filter_status and filter_status != "All":
        query = query.eq("status", filter_status)

    books = query.order("id", desc=True).execute().data

    return render_template("home.html", books=books, results=[], user_key=user_key)


# 🔥 Fetch book data
def fetch_book_data(title):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
        response = requests.get(url).json()

        item = response.get("items", [])[0]
        volume = item.get("volumeInfo", {})

        return {
            "cover_url": volume.get("imageLinks", {}).get("thumbnail"),
            "link": volume.get("infoLink")
        }
    except:
        return {"cover_url": None, "link": None}


@app.route("/add", methods=["POST"])
def add():
    user_key = request.form.get("user")
    title = request.form.get("title")

    book_data = fetch_book_data(title)

    supabase.table("books").insert({
        "user_id": user_key,
        "title": title,
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status"),
        "cover_url": book_data["cover_url"],
        "link": book_data["link"]
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

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url).json()

    results = []
    for item in response.get("items", [])[:5]:
        volume = item.get("volumeInfo", {})

        results.append({
            "title": volume.get("title"),
            "author": ", ".join(volume.get("authors", ["Unknown"])),
            "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
            "link": volume.get("infoLink")
        })

    books = supabase.table("books").select("*").eq("user_id", user_key).order("id", desc=True).execute().data

    return render_template("home.html", books=books, results=results, user_key=user_key)


if __name__ == "__main__":
    app.run(debug=True)
