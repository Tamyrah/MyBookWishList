from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

books = []

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        return redirect(url_for('home', user=name))
    return render_template('login.html')


@app.route('/home', methods=['GET'])
def home():
    user = request.args.get('user')
    query = request.args.get('query')

    results = []

    if query:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}"
        response = requests.get(url)
        data = response.json()

        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})

            title = volume.get('title', 'No Title')
            authors = ', '.join(volume.get('authors', ['Unknown']))
            description = volume.get('description', 'No description available.')

            image_links = volume.get('imageLinks', {})
            thumbnail = image_links.get('thumbnail')

            info_link = volume.get('infoLink', '#')

            results.append({
                'title': title,
                'authors': authors,
                'description': description,
                'thumbnail': thumbnail,
                'link': info_link
            })

    return render_template('home.html', books=books, results=results, user=user)


@app.route('/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    priority = request.form.get('priority')
    status = request.form.get('status')

    books.append({
        'title': title,
        'author': author,
        'genre': genre,
        'priority': priority,
        'status': status
    })

    return redirect(url_for('home', user=request.args.get('user')))


if __name__ == '__main__':
    app.run(debug=True)
