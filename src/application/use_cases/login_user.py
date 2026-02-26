"""
LoginUserUseCase — Autenticação de usuário
"""
from datetime import datetime, timedelta, timezone
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.services.hash_service import HashService
from src.infrastructure.auth.jwt_service import JwtService


class LoginUserUseCase:
    def __init__(self, user_repo: SQLiteUserRepository, hash_svc: HashService, jwt_svc: JwtService):
        self.user_repo = user_repo
        self.hash_svc = hash_svc
        self.jwt_svc = jwt_svc

    def executar(self, username: str, password: str) -> dict:
        user = self.user_repo.buscar_por_username(username)
        if not user or not self.hash_svc.verificar_password(password, user.password_hash):
            raise ValueError('Credenciais inválidas')

        access_token = self.jwt_svc.create_access_token(user.id, user.username)
        refresh_token = self.jwt_svc.create_refresh_token(user.id)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        # Limpa tokens antigos do usuário antes de salvar o novo
        self.user_repo.limpar_tokens_antigos(user.id)
        self.user_repo.salvar_refresh_token(user.id, refresh_token, expires_at)

        return {
            'user': {'id': user.id, 'username': user.username},
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
