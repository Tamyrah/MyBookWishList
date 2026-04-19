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

        print("📩 Email received:", email)

        if not email:
            return jsonify({"error": "Email is required"}), 400

        response = supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": "https://mybookwishlist.onrender.com/home"
            }
        })

        print("✅ Supabase response:", response)

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 ERROR SENDING MAGIC LINK:", str(e))
        return jsonify({"error": str(e)}), 500


# Home Page (after magic link click)
@app.route("/home")
def home():
    return render_template("home.html")


# Receive token from frontend and create session
@app.route("/set_session", methods=["POST"])
def set_session():
    try:
        data = request.get_json()

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        print("🔐 Setting session...")

        supabase.auth.set_session({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

        print("✅ Session set successfully")

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 SESSION ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
