from flask import Flask, request, jsonify, render_template, redirect
from supabase import create_client, Client
import os

app = Flask(__name__)

# 🔐 Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 🟢 ROUTE: LOGIN PAGE
@app.route("/")
def index():
    return render_template("login.html")


# 🟢 ROUTE: SEND MAGIC LINK
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"success": False, "error": "Email is required"})

        # 🔥 Send magic link
        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": "https://mybookwishlist.onrender.com/home"
            }
        })

        return jsonify({"success": True})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False, "error": str(e)})


# 🟢 ROUTE: HOME PAGE (AFTER LOGIN)
@app.route("/home")
def home():
    return render_template("home.html")


# 🟢 SAFETY CHECK ROUTE (OPTIONAL BUT USEFUL)
@app.route("/health")
def health():
    return "OK", 200


# 🚀 RUN APP
if __name__ == "__main__":
    app.run(debug=True)
