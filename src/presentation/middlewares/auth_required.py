"""
auth_required — Decorator que protege endpoints com JWT
"""
import jwt as pyjwt
from functools import wraps
from flask import request, jsonify, g
from src.infrastructure.auth.jwt_service import SECRET_KEY


def auth_required(f):
    """
    Decorator de autenticação JWT.
    Injeta g.user_id e g.username na request após validação.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'status': 'fail', 'data': {'auth': 'Token não fornecido'}}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = pyjwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if payload.get('type') != 'access':
                raise ValueError('Tipo de token inválido')
            g.user_id = payload['sub']
            g.username = payload.get('username', '')
        except pyjwt.ExpiredSignatureError:
            return jsonify({'status': 'fail', 'data': {'auth': 'Token expirado'}}), 401
        except (pyjwt.InvalidTokenError, ValueError):
            return jsonify({'status': 'fail', 'data': {'auth': 'Token inválido'}}), 401

        return f(*args, **kwargs)
    return decorated
