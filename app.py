from flask import Flask, render_template, request, jsonify
from supabase import create_client
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

        # Send magic link email
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


# Home Route (handles token from email link)
@app.route("/home")
def home():
    return render_template("home.html")


# Dashboard Route (THIS loads your REAL app UI)
@app.route("/dashboard")
def dashboard():
    return render_template("home.html")


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
