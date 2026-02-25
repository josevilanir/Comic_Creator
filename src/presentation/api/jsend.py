"""
JSend Wrapper — Padronização de respostas da API REST
Referência: https://github.com/omniti-labs/jsend
"""
from flask import jsonify


def success(data, status_code=200):
    """Resposta de sucesso com dados.
    Ex: return success({"mangas": lista})
    Ex: return success({"message": "Criado!"}, 201)
    """
    return jsonify({"status": "success", "data": data}), status_code


def fail(data, status_code=400):
    """Falha de validação ou erro causado pelo cliente.
    Ex: return fail({"nome": "Campo obrigatório"})
    Ex: return fail({"id": "Não encontrado"}, 404)
    """
    return jsonify({"status": "fail", "data": data}), status_code


def error(message, code="INTERNAL_ERROR", status_code=500):
    """Erro interno inesperado do servidor.
    Ex: return error("Falha ao salvar", "SAVE_ERROR")
    """
    return jsonify({"status": "error", "message": message, "code": code}), status_code
