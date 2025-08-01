import sqlite3
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)"
        )
        db.execute(
            """CREATE TABLE IF NOT EXISTS reads (
                    user_id INTEGER,
                    manga TEXT,
                    chapter TEXT,
                    PRIMARY KEY (user_id, manga, chapter),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )"""
        )
        db.commit()

