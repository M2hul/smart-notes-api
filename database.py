
from contextlib import contextmanager
import sqlite3


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            username TEXT NOT NULL,
            fullname TEXT NOT NULL
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            question TEXT NOT NULL
            )"""
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect("notes.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
