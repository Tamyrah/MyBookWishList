# -----------------------
# ADD (FIXED)
# -----------------------
@app.route("/add", methods=["POST"])
def add_book():
    user_key = request.form.get("user_key")

    # SAFE DEFAULTS (prevents 500 errors)
    title = request.form.get("title", "")
    author = request.form.get("author", "")
    genre = request.form.get("genre", "")
    priority = request.form.get("priority") or "3"
    status = request.form.get("status") or "Want to Read"

    supabase.table("books").insert({
        "user_id": user_key,
        "title": title,
        "author": author,
        "genre": genre,
        "priority": int(priority),
        "status": status
    }).execute()

    return redirect(f"/?user={user_key}")


# -----------------------
# UPDATE (FIXED)
# -----------------------
@app.route("/update", methods=["POST"])
def update_book():
    user_key = request.form.get("user_key")
    book_id = request.form.get("book_id")

    supabase.table("books").update({
        "author": request.form.get("author", ""),
        "genre": request.form.get("genre", ""),
        "priority": int(request.form.get("priority") or 3),
        "status": request.form.get("status") or "Want to Read"
    }).eq("id", book_id).eq("user_id", user_key).execute()

    return redirect(f"/?user={user_key}")


# -----------------------
# REMOVE (FINAL FIX)
# -----------------------
@app.route("/remove", methods=["POST"])
def remove_book():
    user_key = request.form.get("user_key")
    book_id = request.form.get("book_id")

    supabase.table("books")\
        .delete()\
        .eq("id", book_id)\
        .eq("user_id", user_key)\
        .execute()

    return redirect(f"/?user={user_key}")
