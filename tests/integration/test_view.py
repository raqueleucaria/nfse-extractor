import json
import tempfile
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse

from extractor.data_extractor import (
    FileNotFoundError,
    ProcessingError,
    UnsupportedFileTypeError,
)


@pytest.mark.django_db
class TestExtractorViews:
    """Testa a camada de API (views), validando comportamento de cada endpoint."""

    def setup_method(self):
        """Prepara o cliente de testes do Django antes de cada teste."""
        self.client = Client()

    def test_index_view(self):
        """Garante que a página inicial é renderizada com sucesso."""
        response = self.client.get(reverse('extractor:index'))
        assert response.status_code == HTTPStatus.OK
        template_names = [t.name for t in response.templates if t.name]
        assert 'extractor/index.html' in template_names

    def test_hello_api_view(self):
        """Verifica endpoint, status da API online e resposta correta."""
        response = self.client.get(reverse('extractor:hello_api'))
        assert response.status_code == HTTPStatus.OK
        assert response['Content-Type'] == 'application/json'
        data = json.loads(response.content)
        assert data['status'] == 'online'

    def test_extract_api_rejects_non_post_methods(self):
        """Assegura que a API de extração só aceita o método POST."""
        methods = ['GET', 'PUT', 'DELETE', 'PATCH']
        for method in methods:
            response = getattr(self.client, method.lower())(
                reverse('extractor:extract_api')
            )
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
            data = json.loads(response.content)
            assert 'Método não permitido' in data['error']

    def test_extract_api_handles_no_file_sent(self):
        """Valida resposta de erro com nenhum 'file' key enviado no POST."""
        response = self.client.post(reverse('extractor:extract_api'))
        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = json.loads(response.content)
        assert 'Nenhum arquivo. Envie um arquivo no campo "file".' in data['error']

    def test_extract_api_handles_unsupported_file_type(self):
        """Garante que a API rejeita ficheiros com extensões não suportadas."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp_file:
            tmp_file.write(b'conteudo de texto')
            tmp_file.seek(0)
            response = self.client.post(
                reverse('extractor:extract_api'), {'file': tmp_file}
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            data = json.loads(response.content)
            assert 'Tipo de arquivo não suportado' in data['error']

    @patch('extractor.views.extract_nfse_data')
    def test_extract_api_successful_pdf_upload(
        self, mock_extract, uploaded_pdf_file, mock_successful_extraction
    ):
        """Testa o fluxo completo de sucesso para um upload de PDF."""
        mock_extract.return_value = mock_successful_extraction
        response = self.client.post(
            reverse('extractor:extract_api'), {'file': uploaded_pdf_file}
        )
        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data == mock_successful_extraction
        mock_extract.assert_called_once()
        args, _ = mock_extract.call_args
        assert args[1] == 'pdf'

    @patch('extractor.views.extract_nfse_data')
    def test_extract_api_successful_image_upload(
        self, mock_extract, uploaded_image_file, mock_successful_extraction
    ):
        """Valida o fluxo de sucesso para um upload de ficheiro de imagem."""
        mock_extract.return_value = mock_successful_extraction
        response = self.client.post(
            reverse('extractor:extract_api'), {'file': uploaded_image_file}
        )
        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data == mock_successful_extraction
        mock_extract.assert_called_once()
        args, _ = mock_extract.call_args
        assert args[1] == 'image'

    @patch('extractor.views.extract_nfse_data')
    def test_extract_api_handles_custom_extractor_errors(
        self, mock_extract, uploaded_pdf_file
    ):
        """Verifica se a API retorna um erro 400 para qualquer ExtractorError."""
        error_cases = [
            ProcessingError('Erro de processamento simulado'),
            FileNotFoundError('Ficheiro não encontrado simulado'),
            UnsupportedFileTypeError('Tipo incompatível simulado'),
        ]
        for error in error_cases:
            mock_extract.side_effect = error
            response = self.client.post(
                reverse('extractor:extract_api'), {'file': uploaded_pdf_file}
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            data = json.loads(response.content)
            assert str(error) in data['error']

    @patch(
        'extractor.views.extract_nfse_data',
        side_effect=Exception('Erro interno simulado'),
    )
    def test_extract_api_handles_internal_server_error(
        self, mock_extract, uploaded_pdf_file
    ):
        """Garante que a API retorna 500 para erros genéricos e inesperados."""
        response = self.client.post(
            reverse('extractor:extract_api'), {'file': uploaded_pdf_file}
        )
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        data = json.loads(response.content)
        assert 'Erro interno' in data['error']
        assert 'Erro interno simulado' in data['error']

    @patch('extractor.views.extract_nfse_data')
    @patch('os.unlink', side_effect=OSError('Não foi possível apagar o ficheiro'))
    @patch('os.path.exists', return_value=True)
    def test_extract_api_cleanup_fails_gracefully(
        self, mock_exists, mock_unlink, mock_extract, uploaded_pdf_file
    ):
        """
        Assegura que a API não quebra e retorna sucesso para o utilizador,
        mesmo que a limpeza do ficheiro temporário falhe em segundo plano.
        """
        mock_extract.return_value = {'status': 'ok'}

        response = self.client.post(
            reverse('extractor:extract_api'), {'file': uploaded_pdf_file}
        )

        assert response.status_code == HTTPStatus.OK
        mock_unlink.assert_called_once()
