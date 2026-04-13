from flask import Flask, render_template, request, redirect, url_for
from utils import load_wishlist, save_wishlist

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    wishlist = load_wishlist()

    # ADD BOOK
    if request.method == 'POST' and 'add_book' in request.form:
        new_book = {
            "title": request.form.get('title', '').strip(),
            "author": request.form.get('author', '').strip(),
            "genre": request.form.get('genre', '').strip(),
            "priority": request.form.get('priority', '').strip(),
            "status": request.form.get('status', 'Want to Read')
        }

        if new_book["title"]:
            wishlist.append(new_book)
            save_wishlist(wishlist)

        return redirect(url_for('home'))

    # REMOVE BOOK
    if request.method == 'POST' and 'remove_book' in request.form:
        title = request.form.get('title')
        wishlist = [book for book in wishlist if book['title'] != title]
        save_wishlist(wishlist)
        return redirect(url_for('home'))

    # EDIT BOOK
    if request.method == 'POST' and 'edit_book' in request.form:
        original_title = request.form.get('original_title')

        for book in wishlist:
            if book['title'] == original_title:
                book['title'] = request.form.get('title')
                book['author'] = request.form.get('author')
                book['genre'] = request.form.get('genre')
                book['priority'] = request.form.get('priority')
                book['status'] = request.form.get('status')

        save_wishlist(wishlist)
        return redirect(url_for('home'))

    # FILTER
    filter_status = request.args.get('filter', 'All')

    if filter_status != 'All':
        filtered_list = [book for book in wishlist if book.get('status') == filter_status]
    else:
        filtered_list = wishlist

    # SORT BY PRIORITY
    def get_priority(book):
        try:
            return int(book.get('priority', 999))
        except:
            return 999

    filtered_list.sort(key=get_priority)

    return render_template('home.html', wishlist=filtered_list, current_filter=filter_status)


if __name__ == '__main__':
    app.run(debug=True)
