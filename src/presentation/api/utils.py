"""
Utilitários para a camada de apresentação
"""
import os
from flask import current_app, send_file, Response, make_response

def serve_file(file_path, mimetype):
    """
    Serve um arquivo usando send_file ou X-Accel-Redirect se configurado.
    file_path: caminho absoluto no sistema de arquivos
    mimetype: tipo do arquivo
    """
    use_x_accel = current_app.config.get('USE_X_ACCEL_REDIRECT', False)
    
    if use_x_accel:
        # Calcula o caminho relativo à BASE_COMICS
        base_comics = str(current_app.config.get('BASE_COMICS'))
        abs_path = os.path.abspath(file_path)
        abs_base = os.path.abspath(base_comics)
        
        if abs_path.startswith(abs_base):
            relative_path = os.path.relpath(abs_path, abs_base)
            prefix = current_app.config.get('X_ACCEL_PREFIX', '/internal_comics/')
            accel_path = os.path.join(prefix, relative_path)
            
            response = make_response("")
            response.headers['X-Accel-Redirect'] = accel_path
            response.headers['Content-Type'] = mimetype
            return response

    return send_file(file_path, mimetype=mimetype)
