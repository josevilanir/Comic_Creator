import jwt
import bcrypt
import os
from datetime import datetime, timedelta, timezone

# Helper para garantir que a chave seja lida do ambiente sempre que necessário
def get_secret_key():
    return os.environ.get("JWT_SECRET_KEY", "dev-secret-troque-em-producao")

ACCESS_EXPIRES_MINUTES = 30
REFRESH_EXPIRES_DAYS = 7

class JwtService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def create_access_token(user_id: int, username: str) -> str:
        payload = {
            "sub": str(user_id),
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRES_MINUTES),
            "type": "access",
            "jti": os.urandom(8).hex()
        }
        return jwt.encode(payload, get_secret_key(), algorithm="HS256")

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRES_DAYS),
            "type": "refresh",
            "jti": os.urandom(8).hex()
        }
        return jwt.encode(payload, get_secret_key(), algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, get_secret_key(), algorithms=["HS256"])
