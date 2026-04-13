import os
import psycopg2
import json

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def load_wishlist():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id SERIAL PRIMARY KEY,
            data JSONB
        )
    """)

    cur.execute("SELECT data FROM wishlist")
    rows = cur.fetchall()

    wishlist = [row[0] for row in rows]

    cur.close()
    conn.close()

    return wishlist


def save_wishlist(wishlist):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM wishlist")

    for book in wishlist:
        cur.execute(
            "INSERT INTO wishlist (data) VALUES (%s)",
            [json.dumps(book)]
        )

    conn.commit()
    cur.close()
    conn.close()
