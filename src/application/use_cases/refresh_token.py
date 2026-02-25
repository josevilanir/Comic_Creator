import jwt as pyjwt
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository as UserRepository
from src.infrastructure.auth.jwt_service import JwtService
from src.domain.exceptions import InvalidCredentialsException

class RefreshTokenUseCase:
    def __init__(self, repo: UserRepository, jwt_svc: JwtService):
        self.repo = repo
        self.jwt = jwt_svc

    def execute(self, refresh_token: str) -> dict:
        token_record = self.repo.find_refresh_token(refresh_token)
        if not token_record:
            raise InvalidCredentialsException() # Refresh token inválido ou revogado
        
        try:
            payload = self.jwt.decode_token(refresh_token)
        except pyjwt.ExpiredSignatureError:
            self.repo.revoke_refresh_token(refresh_token)
            raise InvalidCredentialsException() # Refresh token expirado
        except pyjwt.InvalidTokenError:
            raise InvalidCredentialsException() # Refresh token inválido
        
        if payload.get("type") != "refresh":
            raise InvalidCredentialsException() # Token inválido
        
        user_id = payload["sub"]
        # Rotation: revogar o antigo, criar novo
        self.repo.revoke_refresh_token(refresh_token)
        
        from datetime import datetime, timedelta, timezone
        
        new_access = self.jwt.create_access_token(user_id, "") # TODO: buscar username se necessário
        new_refresh = self.jwt.create_refresh_token(user_id)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        self.repo.save_refresh_token(user_id, new_refresh, expires_at)
        
        return {"access_token": new_access, "refresh_token": new_refresh}
