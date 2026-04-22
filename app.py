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

def fetch_book_data(title):
    try:
        url = f"https://openlibrary.org/search.json?q={title}&limit=1"
        response = requests.get(url).json()
        doc = response.get("docs", [])[0]
        cover_id = doc.get("cover_i")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
        link = f"https://openlibrary.org/search?q={title.replace(' ', '+')}"
        synopsis = ""
        return {"cover_url": cover_url, "link": link, "synopsis": synopsis}
    except:
        return {"cover_url": None, "link": None, "synopsis": ""}

@app.route("/add", methods=["POST"])
def add():
    user_key = request.form.get("user")
    title = request.form.get("title")
    author = request.form.get("author") or ""

    book_data = fetch_book_data(title)

    fallback_link = f"https://www.google.com/search?q={title.replace(' ', '+')}+{author.replace(' ', '+')}+book"

    supabase.table("books").insert({
    "user_id": user_key,
    "title": title,
    "author": author,
    "genre": request.form.get("genre"),
    "priority": int(request.form.get("priority")),
    "status": request.form.get("status"),
    "cover_url": book_data["cover_url"],
    "link": book_data["link"] if book_data["link"] else fallback_link,
    "synopsis": book_data["synopsis"]
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
    query = request.args.get("q")
    results = []
    if query:
        url = f"https://openlibrary.org/search.json?q={query}&limit=10"
        response = requests.get(url).json()
        for doc in response.get("docs", [])[:10]:
            title = doc.get("title", "No Title")
            author = ", ".join(doc.get("author_name", ["Unknown"]))
            cover_id = doc.get("cover_i")
            thumbnail = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
            results.append({
                "title": title,
                "author": author,
                "description": "",
                "thumbnail": thumbnail,
                "link": f"https://openlibrary.org/search?q={query}"
            })
    books = supabase.table("books").select("*").eq("user_id", user_key).order("id", desc=True).execute().data
    return render_template("home.html", books=books, results=results, user_key=user_key)
if __name__ == "__main__":
    app.run(debug=True)
