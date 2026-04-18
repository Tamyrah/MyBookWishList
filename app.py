from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 🔐 LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")

        supabase.auth.sign_in_with_otp({
            "email": email
        })

        return render_template("login.html", message="Check your email for login link")

    return render_template("login.html")


# 🔁 CALLBACK ROUTE (THIS FIXES YOUR ERROR)
@app.route("/callback")
def callback():
    access_token = request.args.get("access_token")

    if access_token:
        session["user"] = access_token
        return redirect(url_for("home"))

    return redirect(url_for("login"))


# 🏠 HOME
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
