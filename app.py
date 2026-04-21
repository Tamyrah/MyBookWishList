from flask import Flask, render_template, request, jsonify, redirect
from supabase import create_client, Client
import os

app = Flask(__name__)

# 🔐 Supabase setup (make sure these are in Render ENV variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# 🏠 HOME ROUTE
# =========================
@app.route("/")
def index():
    return render_template("login.html")


# =========================
# 🔐 LOGIN ROUTE (FIXED)
# =========================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"success": False, "error": "Email required"})

        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": "https://mybookwishlist.onrender.com/home"
            }
        })

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 LOGIN ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)})


# =========================
# 📚 HOME PAGE AFTER LOGIN
# =========================
@app.route("/home")
def home():
    user_email = request.args.get("user", "")

    # extract name from email
    name = user_email.split("@")[0].capitalize() if user_email else "Reader"

    return render_template("home.html", name=name)


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
