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

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# ROUTES
# -------------------------------

# Login Page
@app.route("/")
def login():
    return render_template("login.html")


# Send Magic Link
@app.route("/send_magic_link", methods=["POST"])
def send_magic_link():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": "https://mybookwishlist.onrender.com/home"
            }
        })

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR SENDING MAGIC LINK:", str(e))
        return jsonify({"error": str(e)}), 500


# Home (used after clicking magic link)
@app.route("/home")
def home():
    return render_template("home.html", results=[])


# Dashboard (MAIN APP)
@app.route("/dashboard")
def dashboard():
    return render_template("home.html", results=[])


# -------------------------------
# SEARCH ROUTE (RESTORES YOUR BOOK SEARCH)
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
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
