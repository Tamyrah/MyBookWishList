import os, json
DATA_FILE = 'wishlist.json'

# Load wishlist from file
def load_wishlist():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save wishlist to file
def save_wishlist(wishlist):
    with open(DATA_FILE, 'w') as f:
        json.dump(wishlist, f)