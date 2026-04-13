import json
import os

FILE_PATH = 'wishlist.json'


def load_wishlist():
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)

            # Ensure all books have required fields
            for book in data:
                book.setdefault("title", "")
                book.setdefault("author", "")
                book.setdefault("genre", "")
                book.setdefault("priority", "")
                book.setdefault("status", "Want to Read")

            return data

    except:
        return []


def save_wishlist(wishlist):
    try:
        with open(FILE_PATH, 'w') as file:
            json.dump(wishlist, file, indent=4)
    except:
        pass
