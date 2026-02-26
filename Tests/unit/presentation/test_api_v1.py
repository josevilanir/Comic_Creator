"""
Testes para API v1 — Formato JSend
"""
import pytest
from unittest.mock import MagicMock
from src.presentation.app import create_app
from src.infrastructure.auth.jwt_service import JwtService


@pytest.fixture
def app():
    app = create_app('development')
    app.config['TESTING'] = True
    app.container = MagicMock()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Gera um Bearer token válido para testes autenticados."""
    secret = app.config.get('JWT_SECRET_KEY')
    token = JwtService(secret).create_access_token(user_id=1, username='testuser')
    return {'Authorization': f'Bearer {token}'}


class TestApiV1:
    def test_get_library_empty(self, client, app, auth_headers):
        app.container.manga_repository.listar_todos.return_value = []
        app.container.manga_repository.contar_todos.return_value = 0

        resp = client.get('/api/v1/library', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['data']['mangas'] == []
        assert data['data']['pagination']['total'] == 0

    def test_get_library_with_data(self, client, app, auth_headers):
        manga = MagicMock()
        manga.nome = "Test Manga"
        manga.tem_capa = False
        manga.total_capitulos = 5
        app.container.manga_repository.listar_todos.return_value = [manga]
        app.container.manga_repository.contar_todos.return_value = 1

        resp = client.get('/api/v1/library', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['mangas']) == 1
        assert data['data']['mangas'][0]['nome'] == "Test Manga"
        assert data['data']['pagination']['total'] == 1

    def test_save_url_validation_fail(self, client, auth_headers):
        resp = client.post('/api/v1/urls', json={}, headers=auth_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'nome' in data['data']
        assert 'url' in data['data']

    def test_save_url_success(self, client, app, auth_headers):
        resp = client.post(
            '/api/v1/urls',
            json={'nome': 'Manga', 'url': 'http://test.com'},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'success'
        assert 'message' in data['data']
        app.container.url_repository.salvar.assert_called_once()

    def test_delete_url_not_found(self, client, app, auth_headers):
        app.container.url_repository.deletar.return_value = False
        resp = client.delete('/api/v1/urls', json={'nome': 'Inexistente'}, headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'nome' in data['data']

    def test_download_chapter_missing_data(self, client, auth_headers):
        resp = client.post('/api/v1/download', json={}, headers=auth_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'message' in data['data']
        assert 'Campos obrigatórios' in data['data']['message']

    def test_get_progresso_not_found(self, client, app, auth_headers):
        app.container.download_job_repository.buscar.return_value = None
        resp = client.get('/api/v1/download/progresso/invalid-id', headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'job_id' in data['data']

    def test_unauthenticated_request_returns_401(self, client):
        """Garante que endpoints protegidos rejeitam requisições sem token."""
        resp = client.get('/api/v1/library')
        assert resp.status_code == 401
        data = resp.get_json()
        assert data['status'] == 'fail'
