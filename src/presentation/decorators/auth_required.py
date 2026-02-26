import jwt as pyjwt
from functools import wraps
from flask import request, jsonify, g, current_app
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        # Suporta Bearer header (API calls) e ?token= query param (<img src> tags)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = request.args.get("token", "")
            if not token:
                return jsonify({"status": "fail", "data": {"auth": "Token não fornecido"}}), 401
        try:
            payload = pyjwt.decode(token, secret_key, algorithms=["HS256"])
            
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
