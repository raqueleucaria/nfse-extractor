import io
import tempfile
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from extractor.data_extractor import ExtractorConfig, NFSeExtractor


@pytest.fixture
def extractor_config():
    """Fixture com configuração padrão do extrator."""
    return ExtractorConfig()


@pytest.fixture
def nfse_extractor(extractor_config):
    """Fixture com instância do extrator."""
    return NFSeExtractor(extractor_config)


@pytest.fixture
def sample_nfse_text():
    """Fixture com texto de exemplo de NFSe."""
    return """
    Dados do Prestador de Serviços
    Razão Social: EMPRESA FICTÍCIA LTDA
    CNPJ: 12.345.678/0001-90
    Nome Fantasia: EMPRESA TESTE
    Dados do Tomador de Serviços
    Razão Social: CLIENTE EXEMPLO LTDA
    """


@pytest.fixture
def invalid_nfse_text():
    """Fixture com texto inválido (sem dados)."""
    return 'Este é um texto sem informações de NFSe'


@pytest.fixture
def temp_dir():
    """Fixture que cria um diretório temporário."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_pdf_file(temp_dir):
    """Fixture que cria um arquivo PDF de teste."""
    pdf_content = (
        b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n'
    )
    pdf_path = temp_dir / 'test.pdf'
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_image_file(temp_dir):
    """Fixture que cria uma imagem de teste."""
    img = Image.new('RGB', (100, 100), color='white')
    img_path = temp_dir / 'test.png'
    img.save(img_path)
    return img_path


@pytest.fixture
def uploaded_pdf_file(sample_nfse_text):
    """Fixture que simula upload de PDF."""
    pdf_content = sample_nfse_text.encode('utf-8')
    return SimpleUploadedFile(
        'test.pdf', pdf_content, content_type='application/pdf'
    )


@pytest.fixture
def uploaded_image_file():
    """Fixture que simula upload de imagem."""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return SimpleUploadedFile(
        'test.png', img_bytes.getvalue(), content_type='image/png'
    )


@pytest.fixture
def mock_successful_extraction():
    """Fixture com resultado esperado de extração."""
    return {
        'cnpj_prestador': '12.345.678/0001-90',
        'nome_prestador': 'EMPRESA FICTÍCIA LTDA',
    }
