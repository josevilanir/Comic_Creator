"""
Testes para API v1 — Formato JSend
"""
import pytest
from src.presentation.app import create_app
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = create_app('development')
    app.config['TESTING'] = True
    
    # Mock container and repositories
    app.container = MagicMock()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

class TestApiV1:
    def test_get_library_empty(self, client, app):
        app.container.manga_repository.listar_todos.return_value = []
        
        resp = client.get('/api/v1/library')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['data'] == []

    def test_get_library_with_data(self, client, app):
        manga = MagicMock()
        manga.nome = "Test Manga"
        manga.tem_capa = False
        manga.total_capitulos = 5
        app.container.manga_repository.listar_todos.return_value = [manga]
        
        resp = client.get('/api/v1/library')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert len(data['data']) == 1
        assert data['data'][0]['nome'] == "Test Manga"

    def test_save_url_validation_fail(self, client):
        resp = client.post('/api/v1/urls', json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'nome' in data['data']
        assert 'url' in data['data']

    def test_save_url_success(self, client, app):
        resp = client.post('/api/v1/urls', json={'nome': 'Manga', 'url': 'http://test.com'})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'success'
        assert 'message' in data['data']
        app.container.url_repository.salvar.assert_called_once()

    def test_delete_url_not_found(self, client, app):
        app.container.url_repository.deletar.return_value = False
        resp = client.delete('/api/v1/urls', json={'nome': 'Inexistente'})
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'nome' in data['data']

    def test_download_chapter_missing_data(self, client):
        resp = client.post('/api/v1/download', json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'base_url' in data['data']

    def test_get_progresso_not_found(self, client):
        resp = client.get('/api/v1/download/progresso/invalid-id')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['status'] == 'fail'
        assert 'job_id' in data['data']
