import sqlite3
import hashlib
from typing import Optional
from src.domain.entities.user import User

DB_PATH = "comic_creator.db"

class UserRepository:
    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token_hash TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    revoked INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_reads (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    PRIMARY KEY (user_id, manga_name, filename),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    PRIMARY KEY (user_id, manga_name, filename),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_urls (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    url_base TEXT NOT NULL,
                    PRIMARY KEY (user_id, manga_name),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    def find_by_username(self, username: str) -> Optional[User]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
        if not row:
            return None
        return User(id=row["id"], username=row["username"],
                    email=row["email"], password_hash=row["password_hash"])

    def find_by_email(self, email: str) -> Optional[User]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        if not row:
            return None
        return User(id=row["id"], username=row["username"],
                    email=row["email"], password_hash=row["password_hash"])

    def create(self, username: str, email: str, password_hash: str) -> User:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            return User(id=cursor.lastrowid, username=username,
                        email=email, password_hash=password_hash)

    def save_refresh_token(self, user_id: int, token: str, expires_at: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
                (user_id, token_hash, expires_at)
            )

    def find_refresh_token(self, token: str) -> Optional[dict]:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM refresh_tokens WHERE token_hash = ? AND revoked = 0",
                (token_hash,)
            ).fetchone()
        return dict(row) if row else None

    def revoke_refresh_token(self, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = ?",
                (token_hash,)
            )

    def revoke_all_tokens(self, user_id: int):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?",
                (user_id,)
            )
