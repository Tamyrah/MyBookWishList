import json
import os

FILE_PATH = 'wishlist.json'


def load_wishlist():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, 'r') as file:
        try:
            data = json.load(file)
            # Ensure every book has a status
            for book in data:
                if 'status' not in book:
                    book['status'] = 'Want to Read'
            return data
        except:
            return []


def save_wishlist(wishlist):
    with open(FILE_PATH, 'w') as file:
        json.dump(wishlist, file, indent=4)
