import os
import psycopg2
import json

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id SERIAL PRIMARY KEY,
            title TEXT,
            author TEXT,
            genre TEXT,
            priority TEXT,
            status TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def load_wishlist():
    init_db()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT title, author, genre, priority, status FROM wishlist")
    rows = cur.fetchall()

    wishlist = []
    for row in rows:
        wishlist.append({
            "title": row[0],
            "author": row[1],
            "genre": row[2],
            "priority": row[3],
            "status": row[4]
        })

    cur.close()
    conn.close()

    return wishlist


def save_wishlist(wishlist):
    init_db()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM wishlist")

    for book in wishlist:
        cur.execute(
            """
            INSERT INTO wishlist (title, author, genre, priority, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                book.get("title"),
                book.get("author"),
                book.get("genre"),
                book.get("priority"),
                book.get("status")
            )
        )

    conn.commit()
    cur.close()
    conn.close()
