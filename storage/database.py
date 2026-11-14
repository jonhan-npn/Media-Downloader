import sqlite3
from pathlib import Path
from app.paths import app_data_dir

DB_PATH = app_data_dir() / "history.sqlite3"

def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                media_format TEXT NOT NULL,
                output_path TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def add_download(title, url, media_format, output_path, status):
    with connect() as db:
        db.execute(
            """INSERT INTO downloads
               (title, url, media_format, output_path, status)
               VALUES (?, ?, ?, ?, ?)""",
            (title, url, media_format, output_path, status),
        )

def get_downloads(limit=500):
    with connect() as db:
        return db.execute(
            "SELECT * FROM downloads ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

def clear_history():
    with connect() as db:
        db.execute("DELETE FROM downloads")
