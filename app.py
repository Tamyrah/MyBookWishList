from flask import Flask, render_template, request, jsonify, redirect
from supabase import create_client
import requests
import os

app = Flask(__name__)

# -------------------------------
# Supabase Setup
# -------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/send_magic_link", methods=["POST"])
def send_magic_link():
    try:
        data = request.get_json()
        email = data.get("email")

        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": "https://mybookwishlist.onrender.com/home"
            }
        })

        return jsonify({"success": True})

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/home")
def home():
    return render_template("home.html", results=[])


@app.route("/dashboard")
def dashboard():
    return render_template("home.html", results=[])


# -------------------------------
# SEARCH (FIXED)
# -------------------------------
@app.route("/search")
def search():
    try:
        query = request.args.get("query")

        if not query:
            return render_template("home.html", results=[])

        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url)
        data = response.json()

        results = []

        if "items" in data:
            for item in data["items"]:
                volume = item.get("volumeInfo", {})

                results.append({
                    "title": volume.get("title", "No Title"),
                    "author": ", ".join(volume.get("authors", ["Unknown"])),
                    "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
                    "link": volume.get("infoLink"),
                    "description": volume.get("description", "No description available")
                })

        return render_template("home.html", results=results)

    except Exception as e:
        print("SEARCH ERROR:", str(e))
        return render_template("home.html", results=[])


# -------------------------------
# ADD BOOK (FIXES 404)
# -------------------------------
@app.route("/add_book", methods=["POST"])
def add_book():
    try:
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        priority = request.form.get("priority")
        status = request.form.get("status")

        print("BOOK ADDED:", title, author, genre, priority, status)

        return redirect("/dashboard")

    except Exception as e:
        print("ADD BOOK ERROR:", str(e))
        return redirect("/dashboard")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
