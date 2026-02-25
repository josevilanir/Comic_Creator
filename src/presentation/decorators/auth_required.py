import jwt as pyjwt
from functools import wraps
from flask import request, jsonify, g, current_app
from src.infrastructure.auth.jwt_service import get_secret_key

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"status": "fail", "data": {"auth": "Token não fornecido"}}), 401
        
        token = auth_header.split(" ")[1]
        try:
            secret = get_secret_key()
            payload = pyjwt.decode(token, secret, algorithms=["HS256"])
            
            if payload.get("type") != "access":
                return jsonify({"status": "fail", "data": {"auth": "Tipo de token inválido"}}), 401
                
            g.user_id = payload["sub"]
            g.username = payload.get("username")
            
        except pyjwt.ExpiredSignatureError:
            return jsonify({"status": "fail", "data": {"auth": "Token expirado"}}), 401
        except pyjwt.InvalidTokenError as e:
            return jsonify({"status": "fail", "data": {"auth": f"Token inválido: {str(e)}"}}), 401
        except Exception as e:
            return jsonify({"status": "fail", "data": {"auth": "Erro interno de autenticação"}}), 401
        
        return f(*args, **kwargs)
    return decorated
