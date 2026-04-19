from flask import Flask, render_template, request, jsonify
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
    data = request.get_json()
    email = data.get("email")

    supabase.auth.sign_in_with_otp({
        "email": email,
        "options": {
            "email_redirect_to": "https://mybookwishlist.onrender.com/home"
        }
    })

    return jsonify({"success": True})


@app.route("/home")
def home():
    return render_template("home.html", results=[])


@app.route("/dashboard")
def dashboard():
    return render_template("home.html", results=[])


# -------------------------------
# 🔍 SEARCH ROUTE (THIS FIXES YOUR ERROR)
# -------------------------------
@app.route("/search")
def search():
    query = request.args.get("query")

    if not query:
        return render_template("home.html", results=[])

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"

    response = requests.get(url)
    data = response.json()

    results = []

    if "items" in data:
        for item in data["items"]:
            volume = item["volumeInfo"]

            results.append({
                "title": volume.get("title"),
                "author": ", ".join(volume.get("authors", ["Unknown"])),
                "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
                "link": volume.get("infoLink")
            })

    return render_template("home.html", results=results)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
