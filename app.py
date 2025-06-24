from flask import Flask, render_template, request, redirect, url_for
from utils import load_wishlist, save_wishlist


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    wishlist = load_wishlist()
    if request.method == 'POST':
        new_book = {
            "title": request.form.get('title', '').strip(),
            "author": request.form.get('author', '').strip(),
            "genre": request.form.get('genre', '').strip(),
            "priority": request.form.get('priority', '').strip()
        }
        if new_book["title"]:  # Only save if title exists
            wishlist.append(new_book)
            save_wishlist(wishlist)
            return redirect(url_for('home'))
    return render_template('home.html', wishlist=wishlist)

@app.route('/remove', methods=['POST'])
def remove_book():
    wishlist = load_wishlist()
    title_to_remove = request.form.get('title')
    wishlist = [book for book in wishlist if book['title'] != title_to_remove]
    save_wishlist(wishlist)
    return redirect(url_for('home'))


@app.route('/remove/<int:index>', methods=['POST'])
def remove(index):
    wishlist = load_wishlist()
    if 0 <= index < len(wishlist):
        wishlist.pop(index)
        save_wishlist(wishlist)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)



