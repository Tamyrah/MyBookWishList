from flask import Flask, render_template, request, redirect
from supabase import create_client
import os

app = Flask(__name__)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def home():
    user = request.args.get("user")

    if not user:
        return render_template("enter.html")

    # ADD BOOK
    if request.method == "POST":
        supabase.table("books").insert({
            "title": request.form.get("title"),
            "author": request.form.get("author"),
            "genre": request.form.get("genre"),
            "priority": int(request.form.get("priority")),
            "status": request.form.get("status"),
            "user_id": user
        }).execute()

    # BASE QUERY (ALWAYS FILTER BY USER)
    query = supabase.table("books").select("*").eq("user_id", user)

    # FILTER
    status = request.args.get("status")
    if status:
        query = query.eq("status", status)

    # SEARCH (FIXED — DOES NOT BREAK LIST)
    search = request.args.get("query")
    if search:
        query = query.ilike("title", f"%{search}%")

    response = query.order("id", desc=True).execute()
    books = response.data if response.data else []

    return render_template("home.html", books=books, user=user)


# UPDATE
@app.route("/update", methods=["POST"])
def update():
    book_id = request.form.get("id")
    user = request.form.get("user")

    supabase.table("books").update({
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": int(request.form.get("priority")),
        "status": request.form.get("status"),
    }).eq("id", book_id).execute()

    return redirect(f"/?user={user}")


# DELETE (FIXED)
@app.route("/delete", methods=["POST"])
def delete():
    book_id = request.form.get("id")
    user = request.form.get("user")

    supabase.table("books").delete().eq("id", book_id).execute()

    return redirect(f"/?user={user}")


# ENTER NAME
@app.route("/enter", methods=["GET", "POST"])
def enter():
    if request.method == "POST":
        user = request.form.get("user")
        return redirect(f"/?user={user}")

    return render_template("enter.html")


if __name__ == "__main__":
    app.run(debug=True)
