from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"


# 🔗 Supabase connection
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 🔐 LOGIN ROUTE
@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email")

        try:
            supabase.auth.sign_in_with_otp({
                "email": email
            })
            message = "Check your email for your login link"
        except Exception as e:
            print("LOGIN ERROR:", e)
            message = "Something went wrong. Try again."

    return render_template("login.html", message=message)


# 🏠 HOME ROUTE
@app.route("/home")
def home():
    # token comes from login.html redirect
    token = request.args.get("token")

    if token:
        session["user"] = token

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
