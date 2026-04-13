from flask import Flask, render_template, request, redirect, url_for

app = Flask(**name**)

# In-memory database (simple for now)

wishlist = []

@app.route("/", methods=["GET", "POST"])
def home():
global wishlist

```
if request.method == "POST":
    new_book = {
        "title": request.form.get("title"),
        "author": request.form.get("author"),
        "genre": request.form.get("genre"),
        "priority": request.form.get("priority"),
        "status": request.form.get("status")
    }
    wishlist.append(new_book)
    return redirect(url_for("home"))

filter_status = request.args.get("filter")

if filter_status and filter_status != "All":
    filtered_list = [book for book in wishlist if book["status"] == filter_status]
else:
    filtered_list = wishlist

return render_template("home.html", wishlist=filtered_list)
```

@app.route("/remove", methods=["POST"])
def remove_book():
global wishlist
title = request.form.get("title")

```
wishlist = [book for book in wishlist if book["title"] != title]

return redirect(url_for("home"))
```

@app.route("/edit", methods=["POST"])
def edit_book():
global wishlist
original_title = request.form.get("original_title")

```
for book in wishlist:
    if book["title"] == original_title:
        book["title"] = request.form.get("title")
        book["author"] = request.form.get("author")
        book["genre"] = request.form.get("genre")
        book["priority"] = request.form.get("priority")
        book["status"] = request.form.get("status")

return redirect(url_for("home"))
```

if **name** == "**main**":
app.run(debug=True)

