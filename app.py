from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "leaflist_secret_key"

wishlist = []


@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    global wishlist

    if request.method == "POST":
        new_book = {
            "title": request.form.get("title"),
            "author": request.form.get("author"),
            "genre": request.form.get("genre"),
            "priority": request.form.get("priority"),
            "status": request.form.get("status")
        }
        wishlist.append(new_book)
        return redirect("/")

    filter_status = request.args.get("filter")

    if filter_status and filter_status != "All":
        filtered_list = [book for book in wishlist if book["status"] == filter_status]
    else:
        filtered_list = wishlist

    return render_template("home.html", wishlist=filtered_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            session["user"] = email
            return redirect("/")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/login")

    return render_template("register.html")


@app.route("/remove", methods=["POST"])
def remove_book():
    global wishlist
    title = request.form.get("title")
    wishlist = [book for book in wishlist if book["title"] != title]
    return redirect("/")


@app.route("/edit", methods=["POST"])
def edit_book():
    global wishlist
    original_title = request.form.get("original_title")

    for book in wishlist:
        if book["title"] == original_title:
            book["title"] = request.form.get("title")
            book["author"] = request.form.get("author")
            book["genre"] = request.form.get("genre")
            book["priority"] = request.form.get("priority")
            book["status"] = request.form.get("status")

    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
