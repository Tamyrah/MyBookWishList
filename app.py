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
    try:
        res = supabase.table("books").select("*").eq("user_id", user_key).execute()
        books = res.data or []
    except Exception as e:
        print("HOME ERROR:", e)
        books = []
    return render_template("home.html", books=books, results=[], user_key=user_key)

@app.route("/add", methods=["POST"])
def add():
    user_key = request.form.get("user")
    try:
        supabase.table("books").insert({
            "user_id": user_key,
            "title": request.form.get("title"),
            "author": request.form.get("author"),
            "genre": request.form.get("genre"),
            "priority": int(request.form.get("priority")),
            "status": request.form.get("status")
        }).execute()
    except Exception as e:
        print("ADD ERROR:", e)
    return redirect(f"/home?user={user_key}")

@app.route("/update", methods=["POST"])
def update():
    user_key = request.form.get("user")
    book_id = request.form.get("id")
    try:
        supabase.table("books").update({
            "author": request.form.get("author"),
            "genre": request.form.get("genre"),
            "priority": int(request.form.get("priority")),
            "status": request.form.get("status")
        }).eq("id", book_id).execute()
    except Exception as e:
        print("UPDATE ERROR:", e)
    return redirect(f"/home?user={user_key}")

@app.route("/remove", methods=["POST"])
def remove():
    user_key = request.form.get("user")
    book_id = request.form.get("id")
    try:
        supabase.table("books").delete().eq("id", book_id).execute()
    except Exception as e:
        print("REMOVE ERROR:", e)
    return redirect(f"/home?user={user_key}")

@app.route("/search")
def search():
    user_key = request.args.get("user")
    query = request.args.get("query")

    results = []
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url).json()

        for item in response.get("items", [])[:5]:
            volume = item.get("volumeInfo", {})
            results.append({
                "title": volume.get("title"),
                "author": ", ".join(volume.get("authors", ["Unknown"])),
                "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
                "description": volume.get("description", "")[:200]
            })
    except Exception as e:
        print("SEARCH ERROR:", e)

    try:
        res = supabase.table("books").select("*").eq("user_id", user_key).execute()
        books = res.data or []
    except Exception as e:
        print("BOOK FETCH ERROR:", e)
        books = []

    return render_template("home.html", books=books, results=results, user_key=user_key)

if __name__ == "__main__":
    app.run(debug=True)
