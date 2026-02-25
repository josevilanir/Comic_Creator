"""
SQLite User Repository - Implementação oficial usando SQLite
"""
import sqlite3
import hashlib
from typing import Optional, List
from src.domain.entities.user import User
from src.domain.repositories.interfaces import IUserRepository

class SQLiteUserRepository(IUserRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Migração: Garantir que todas as colunas existam
            cursor = conn.execute("PRAGMA table_info(users)")
            colunas = [row[1] for row in cursor.fetchall()]
            
            if 'email' not in colunas:
                conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
                try:
                    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                except: pass

            if 'password_hash' not in colunas:
                conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

            if 'created_at' not in colunas:
                conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT (datetime('now'))")
            
            if 'updated_at' not in colunas:
                conn.execute("ALTER TABLE users ADD COLUMN updated_at TEXT DEFAULT (datetime('now'))")

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

    def create(self, user: User) -> User:
        # email pode ser None — SQLite UNIQUE permite múltiplos NULLs
        email_val = user.email if user.email else None
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (user.username, email_val, user.password_hash)
            )
            user.id = cursor.lastrowid
            return user

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

    def buscar_por_username(self, username: str) -> Optional[User]:
        return self.find_by_username(username)

    def buscar_por_id(self, user_id: int) -> Optional[User]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row: return None
        return User(id=row["id"], username=row["username"], email=row["email"], password_hash=row["password_hash"])

    def revogar_todos_tokens(self, user_id: int):
        with self._get_conn() as conn:
            conn.execute(
                'UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?',
                (user_id,)
            )

    # ── Aliases em português para os use cases do MVP ─────────────────────────
    def salvar_refresh_token(self, user_id: int, token: str, expires_at: str):
        return self.save_refresh_token(user_id, token, expires_at)

    def buscar_refresh_token(self, token: str) -> Optional[dict]:
        return self.find_refresh_token(token)

    def revogar_refresh_token(self, token: str):
        return self.revoke_refresh_token(token)

    def atualizar(self, user: User) -> User: return user # Dummy para interface
    def existe(self, username: str) -> bool: return self.find_by_username(username) is not None
    def listar_todos(self) -> List[User]: return []
    def criar(self, user: User) -> User: return self.create(user)
