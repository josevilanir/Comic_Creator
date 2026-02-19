"""
Testes para Error Handlers
"""
import pytest
from src.presentation.app import create_app
from src.domain.exceptions import (
    MangaNaoEncontradoException,
    MangaJaExisteException,
    ValidationException as DomainValidationException,
)


@pytest.fixture
def client():
    app = create_app('development')
    app.config['TESTING'] = True
    client = app.test_client()
    return client


class TestErrorHandlers:
    def test_manga_nao_encontrado(self, client):
        @client.application.route('/_test/not_found')
        def _raise():
            raise MangaNaoEncontradoException('Inexistente')

        resp = client.get('/_test/not_found')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['sucesso'] is False
        assert 'não encontrado' in data['erro'].lower()

    def test_manga_duplicado(self, client):
        @client.application.route('/_test/duplicate')
        def _raise_dup():
            raise MangaJaExisteException('Test')

        resp = client.get('/_test/duplicate')
        assert resp.status_code == 409
        data = resp.get_json()
        assert data['sucesso'] is False
        assert 'já existe' in data['erro'].lower()

    def test_domain_validation(self, client):
        @client.application.route('/_test/validation')
        def _raise_val():
            raise DomainValidationException('Campo inválido', field='nome')

        resp = client.get('/_test/validation')
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['sucesso'] is False
        assert data['codigo'] == 'VALIDATION_ERROR'
        assert data.get('campo') == 'nome'
