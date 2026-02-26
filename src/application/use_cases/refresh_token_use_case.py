"""
RefreshTokenUseCase — Rotação de refresh token
"""
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.auth.jwt_service import JwtService


class RefreshTokenUseCase:
    def __init__(self, user_repo: SQLiteUserRepository, jwt_svc: JwtService):
        self.user_repo = user_repo
        self.jwt_svc = jwt_svc

    def executar(self, refresh_token: str) -> dict:
        record = self.user_repo.buscar_refresh_token(refresh_token)
        if not record:
            raise ValueError('Refresh token inválido ou revogado')

        try:
            payload = self.jwt_svc.decode_token(refresh_token)
        except pyjwt.ExpiredSignatureError:
            self.user_repo.revogar_refresh_token(refresh_token)
            raise ValueError('Refresh token expirado')
        except pyjwt.InvalidTokenError:
            raise ValueError('Refresh token inválido')

        if payload.get('type') != 'refresh':
            raise ValueError('Tipo de token inválido')

        user_id = payload['sub']
        username = payload.get('username', '')

        # Rotação: revogar o antigo, emitir novo par
        self.user_repo.revogar_refresh_token(refresh_token)
        self.user_repo.limpar_tokens_antigos(user_id)

        new_access = self.jwt_svc.create_access_token(user_id, username)
        new_refresh = self.jwt_svc.create_refresh_token(user_id)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        self.user_repo.salvar_refresh_token(user_id, new_refresh, expires_at)

        return {'access_token': new_access, 'refresh_token': new_refresh}
