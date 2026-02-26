"""
JWT Service — Geração e validação de tokens JWT
"""
import jwt
import uuid
from datetime import datetime, timedelta, timezone

ACCESS_EXPIRES_MINUTES = 30
REFRESH_EXPIRES_DAYS = 7


class JwtService:
    """Serviço de JWT — encode/decode de access e refresh tokens."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def create_access_token(self, user_id: int, username: str) -> str:
        payload = {
            'sub': user_id,
            'username': username,
            'type': 'access',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRES_MINUTES),
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def create_refresh_token(self, user_id: int) -> str:
        payload = {
            'sub': user_id,
            'type': 'refresh',
            'jti': str(uuid.uuid4()),  # garante unicidade mesmo quando chamado no mesmo segundo
            'exp': datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRES_DAYS),
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def decode_token(self, token: str) -> dict:
        """
        Decodifica token. Lança jwt.ExpiredSignatureError ou jwt.InvalidTokenError em caso de falha.
        """
        return jwt.decode(token, self.secret_key, algorithms=['HS256'])
