"""
RegisterUserUseCase — Registro de novo usuário
"""
from datetime import datetime, timedelta, timezone
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.services.hash_service import HashService
from src.infrastructure.auth.jwt_service import JwtService


class RegisterUserUseCase:
    def __init__(self, user_repo: SQLiteUserRepository, hash_svc: HashService, jwt_svc: JwtService):
        self.user_repo = user_repo
        self.hash_svc = hash_svc
        self.jwt_svc = jwt_svc

    def executar(self, username: str, password: str) -> dict:
        valido, msg = self.hash_svc.validar_forca_senha(password)
        if not valido:
            raise ValueError(msg)

        if self.user_repo.existe(username):
            raise ValueError('Username já em uso')

        password_hash = self.hash_svc.hash_password(password)
        # email é opcional — passa None (SQLite UNIQUE permite múltiplos NULLs)
        user = self.user_repo.criar(User(id=None, username=username, email=None, password_hash=password_hash))

        access_token = self.jwt_svc.create_access_token(user.id, user.username)
        refresh_token = self.jwt_svc.create_refresh_token(user.id)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        self.user_repo.salvar_refresh_token(user.id, refresh_token, expires_at)

        return {
            'user': {'id': user.id, 'username': user.username},
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
