from flask import Flask, render_template, request, redirect
from supabase import create_client
import os

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/", methods=["GET", "POST"])
def home():
    user = request.args.get("user")

    if not user:
        return render_template("enter.html")

    # ADD BOOK
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        priority = int(request.form.get("priority"))
        status = request.form.get("status")

        supabase.table("books").insert({
            "title": title,
            "author": author,
            "genre": genre,
            "priority": priority,
            "status": status,
            "user_id": user
        }).execute()

        return redirect(f"/?user={user}")

    # FILTER + SEARCH
    query = request.args.get("query")
    status_filter = request.args.get("status")

    response = supabase.table("books").select("*").eq("user_id", user)

    if status_filter:
        response = response.eq("status", status_filter)

    books = response.execute().data

    if query:
        books = [b for b in books if query.lower() in b["title"].lower()]

    return render_template("home.html", books=books, user=user)


# UPDATE BOOK
@app.route("/update", methods=["POST"])
def update():
    user = request.form.get("user")
    book_id = request.form.get("id")

    supabase.table("books").update({
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status"),
    }).eq("id", book_id).execute()

    return redirect(f"/?user={user}")


# DELETE BOOK
@app.route("/delete", methods=["POST"])
def delete():
    user = request.form.get("user")
    book_id = request.form.get("id")

    supabase.table("books").delete().eq("id", book_id).execute()

    return redirect(f"/?user={user}")


# ENTER NAME
@app.route("/enter", methods=["POST"])
def enter():
    name = request.form.get("name")
    return redirect(f"/?user={name}")


if __name__ == "__main__":
    app.run()
