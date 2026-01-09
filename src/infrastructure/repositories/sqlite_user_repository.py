"""
SQLite User Repository - Implementação de repositório de usuários com SQLite
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from ...domain.entities import User
from ...domain.repositories import IUserRepository
from ...domain.exceptions import UserAlreadyExistsException


class SQLiteUserRepository(IUserRepository):
    """
    Repositório de usuários usando SQLite.
    
    Tabela:
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        data_criacao DATETIME,
        ultimo_acesso DATETIME
    );
    """
    
    def __init__(self, database_path: str = 'comic_creator.db'):
        """
        Args:
            database_path: Caminho do arquivo SQLite
        """
        self.database_path = database_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa tabela de usuários se não existir"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def criar(self, user: User) -> User:
        """
        Cria um novo usuário.
        
        Raises:
            UserAlreadyExistsException: Se username já existe
        """
        if self.existe(user.username):
            raise UserAlreadyExistsException(user.username)
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''
                INSERT INTO users (username, password_hash, data_criacao)
                VALUES (?, ?, ?)
                ''',
                (user.username, user.password_hash, datetime.now())
            )
            
            user.id = cursor.lastrowid
            user.data_criacao = datetime.now()
            
            conn.commit()
            return user
            
        except sqlite3.IntegrityError:
            raise UserAlreadyExistsException(user.username)
        finally:
            conn.close()
    
    def buscar_por_username(self, username: str) -> Optional[User]:
        """Busca usuário pelo username"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_user(row)
        
        return None
    
    def buscar_por_id(self, user_id: int) -> Optional[User]:
        """Busca usuário pelo ID"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_user(row)
        
        return None
    
    def atualizar(self, user: User) -> User:
        """Atualiza dados do usuário"""
        if not user.id:
            raise ValueError("User deve ter ID para atualizar")
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            UPDATE users
            SET username = ?,
                password_hash = ?,
                ultimo_acesso = ?
            WHERE id = ?
            ''',
            (user.username, user.password_hash, user.ultimo_acesso, user.id)
        )
        
        conn.commit()
        conn.close()
        
        return user
    
    def existe(self, username: str) -> bool:
        """Verifica se usuário existe"""
        return self.buscar_por_username(username) is not None
    
    def listar_todos(self) -> List[User]:
        """Lista todos os usuários"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY username')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_user(row) for row in rows]
    
    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Converte row do SQLite para entidade User"""
        data_criacao = None
        if row['data_criacao']:
            try:
                data_criacao = datetime.fromisoformat(row['data_criacao'])
            except Exception:
                pass
        
        ultimo_acesso = None
        if row['ultimo_acesso']:
            try:
                ultimo_acesso = datetime.fromisoformat(row['ultimo_acesso'])
            except Exception:
                pass
        
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            data_criacao=data_criacao,
            ultimo_acesso=ultimo_acesso
        )