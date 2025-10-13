from unittest.mock import MagicMock, patch

import pytesseract
import pytest
from pdfminer.pdfparser import PDFSyntaxError

from extractor.data_extractor import (
    ExtractorConfig,
    FileNotFoundError,
    ImageReader,
    NFSeExtractor,
    PDFReader,
    ProcessingError,
    Reader,
    UnsupportedFileTypeError,
    extract_nfse_data,
    get_reader,
)


class TestReaderBaseClass:
    """Testa o contrato da classe base 'Reader'."""

    def test_read_base_raises_not_implemented_error(self):
        """Garante que a classe base não pode ser usada diretamente."""
        reader = Reader()
        with pytest.raises(NotImplementedError):
            reader.read('qualquer/caminho')


class TestPDFReader:
    """Valida o leitor de arquivos PDF em cenários de sucesso e falha."""

    def test_read_raises_file_not_found(self):
        """Verifica se a exceção correta é mostrada para um arquivo inexistente."""
        reader = PDFReader()
        non_existent_file = 'caminho/garantidamente/inexistente.pdf'
        with pytest.raises(FileNotFoundError, match='Arquivo PDF não encontrado'):
            reader.read(non_existent_file)

    @patch('pdfplumber.open')
    def test_pdf_reader_successful(self, mock_pdfplumber_open, temp_dir):
        """Simula uma leitura de PDF bem-sucedida, validando a extração."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = 'Texto da página 1'
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        reader = PDFReader()
        pdf_path = temp_dir / 'test.pdf'
        pdf_path.touch()

        text = reader.read(str(pdf_path))

        assert text == 'Texto da página 1'

    @patch('pdfplumber.open')
    def test_pdf_reader_no_pages(self, mock_pdfplumber_open, temp_dir):
        """Garante que um erro é lançado ao processar um PDF sem páginas."""
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        reader = PDFReader()
        pdf_path = temp_dir / 'no_pages.pdf'
        pdf_path.touch()

        with pytest.raises(
            ProcessingError, match='PDF não contém páginas válidas'
        ):
            reader.read(str(pdf_path))

    @patch('pdfplumber.open')
    def test_pdf_reader_no_extractable_text(self, mock_pdfplumber_open, temp_dir):
        """Testa PDF existente, mas sem texto extraível."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = '   '
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

        reader = PDFReader()
        pdf_path = temp_dir / 'image_only.pdf'
        pdf_path.touch()

        with pytest.raises(
            ProcessingError, match='Não foi possível extrair texto do PDF'
        ):
            reader.read(str(pdf_path))

    @patch('pdfplumber.open', side_effect=PDFSyntaxError('Ficheiro corrompido'))
    def test_pdf_reader_syntax_error(self, mock_pdfplumber_open, temp_dir):
        """Valida o tratamento de erro para arquivos PDF corrompidos."""
        reader = PDFReader()
        pdf_path = temp_dir / 'corrupted.pdf'
        pdf_path.touch()

        with pytest.raises(ProcessingError, match='Arquivo PDF corrompido'):
            reader.read(str(pdf_path))

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pdfplumber.open', side_effect=PermissionError('Acesso negado'))
    def test_pdf_reader_permission_error(self, mock_open, mock_exists):
        """Simula erro de permissão do SO ao tentar ler o arquivo."""
        reader = PDFReader()
        with pytest.raises(
            ProcessingError, match='Sem permissão para ler o arquivo'
        ):
            reader.read('caminho/protegido.pdf')

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pdfplumber.open', side_effect=Exception('Erro genérico'))
    def test_pdf_reader_generic_exception(self, mock_open, mock_exists):
        """Garante que qualquer erro inesperado durante a leitura é capturado."""
        reader = PDFReader()
        with pytest.raises(
            ProcessingError, match='Erro inesperado ao processar o PDF'
        ):
            reader.read('caminho/qualquer.pdf')


class TestImageReader:
    """Valida o leitor de imagens (OCR) em diversos cenários."""

    def test_read_raises_file_not_found(self):
        """Verifica se a exceção correta é mostrada para uma imagem inexistente."""
        reader = ImageReader()
        non_existent_file = 'caminho/imagem/inexistente.png'
        with pytest.raises(
            FileNotFoundError, match='Arquivo de imagem não encontrado'
        ):
            reader.read(non_existent_file)

    @patch('PIL.Image.open')
    @patch('pytesseract.image_to_string', return_value='Texto da imagem')
    def test_image_reader_successful(self, mock_ocr, mock_open, temp_dir):
        """Simula uma leitura de imagem com OCR bem-sucedida."""
        reader = ImageReader()
        image_path = temp_dir / 'test.png'
        image_path.touch()
        text = reader.read(str(image_path))
        assert text == 'Texto da imagem'

    @patch('PIL.Image.open')
    @patch('pytesseract.image_to_string', return_value='  ')
    def test_image_reader_no_extractable_text(self, mock_ocr, mock_open, temp_dir):
        """Testa o caso de uma imagem da qual o OCR não consegue extrair texto."""
        reader = ImageReader()
        image_path = temp_dir / 'blank.png'
        image_path.touch()
        with pytest.raises(
            ProcessingError, match='Não foi possível extrair texto da imagem'
        ):
            reader.read(str(image_path))

    @patch('pathlib.Path.exists', return_value=True)
    @patch('PIL.Image.open')
    @patch(
        'pytesseract.image_to_string',
        side_effect=pytesseract.TesseractNotFoundError,
    )
    def test_image_reader_tesseract_not_found(
        self, mock_ocr, mock_image_open, mock_exists
    ):
        """Simula o cenário onde o Tesseract OCR não está instalado no sistema."""
        reader = ImageReader()
        with pytest.raises(ProcessingError, match='Tesseract OCR não instalado'):
            reader.read('qualquer/imagem.png')

    @patch('pathlib.Path.exists', return_value=True)
    @patch('PIL.Image.open', side_effect=Exception('Formato de imagem inválido'))
    def test_image_reader_invalid_image_format(self, mock_open, mock_exists):
        """Valida o tratamento de erro para imagens inválidas."""
        reader = ImageReader()
        with pytest.raises(
            ProcessingError, match='Arquivo não é uma imagem válida'
        ):
            reader.read('imagem_corrompida.jpg')

    @patch('pathlib.Path.exists', return_value=True)
    @patch('PIL.Image.open', side_effect=PermissionError('Acesso negado'))
    def test_image_reader_permission_error(self, mock_open, mock_exists):
        """Simula um erro de permissão do sistema operacional ao ler a imagem."""
        reader = ImageReader()
        with pytest.raises(
            ProcessingError, match='Sem permissão para ler o arquivo'
        ):
            reader.read('caminho/protegido.png')


class TestNFSeExtractor:
    """Testa a lógica de extração de dados a partir de uma string de texto."""

    def test_extract_from_text_successful(
        self, nfse_extractor, sample_nfse_text, mock_successful_extraction
    ):
        """Valida o 'caminho feliz' da extração, com um texto bem formatado."""
        result = nfse_extractor.extract_from_text(sample_nfse_text)
        assert result == mock_successful_extraction

    def test_init_with_no_config(self):
        """Garante que o extrator usa uma configuração padrão."""
        extractor = NFSeExtractor(config=None)
        assert isinstance(extractor.config, ExtractorConfig)

    def test_isolate_section_without_start_marker(self, nfse_extractor):
        """Testa comportamento com marcador de início da seção não encontrado."""
        text = 'Texto sem a seção do prestador'
        result = nfse_extractor._isolate_prestador_section(text)
        assert result == text

    def test_isolate_section_with_end_marker(self, nfse_extractor):
        """Valida isolamento quando os marcadores de início e fim existem."""
        text = 'Dados do Prestador de Serviços... SECÇÃO... Dados do Tomador'
        result = nfse_extractor._isolate_prestador_section(text)
        assert 'Dados do Tomador' not in result
        assert result.strip() == '... SECÇÃO...'

    def test_isolate_section_without_end_marker(self, nfse_extractor):
        """Valida isolamento de texto quando só o marcador de início existe."""
        text = 'Dados do Prestador de Serviços... e nada mais'
        expected = '... e nada mais'
        result = nfse_extractor._isolate_prestador_section(text)
        assert result.strip() == expected.strip()

    def test_extract_cnpj_not_found(self, nfse_extractor):
        """Verifica resultado nulo para CNPJ não encontrado no texto."""
        result = nfse_extractor._extract_cnpj('Texto sem CNPJ')
        assert result is None

    def test_extract_razao_social_not_found(self, nfse_extractor):
        """Verifica resultado nulo para Razão Social não encontrada."""
        result = nfse_extractor._extract_razao_social('Texto sem Razão Social')
        assert result is None


class TestGetReader:
    """Testa a 'factory' que seleciona o leitor de arquivo correto."""

    def test_get_reader_returns_pdf_reader(self):
        """Garante que a factory retorna um PDFReader para o tipo 'pdf'."""
        assert isinstance(get_reader('pdf'), PDFReader)
        assert isinstance(get_reader('PDF'), PDFReader)

    def test_get_reader_returns_image_reader(self):
        """Garante que a factory retorna um ImageReader para o tipo 'image'."""
        assert isinstance(get_reader('image'), ImageReader)

    def test_get_reader_raises_error_for_unsupported_type(self):
        """Verifica se um erro é lançado para tipos de arquivo não suportados."""
        with pytest.raises(UnsupportedFileTypeError):
            get_reader('docx')


class TestExtractNFSeData:
    """Testa a função orquestradora que integra todas as partes do sistema."""

    def test_extract_nfse_data_file_not_found(self):
        """Verifica se a função principal lida com arquivos inexistentes."""
        with pytest.raises(FileNotFoundError):
            extract_nfse_data('caminho/inexistente.pdf', 'pdf')

    @patch('extractor.data_extractor.get_reader')
    @patch('extractor.data_extractor.NFSeExtractor')
    def test_extract_nfse_data_successful_flow(
        self,
        mock_extractor_class,
        mock_get_reader,
        temp_dir,
        mock_successful_extraction,
    ):
        """Testa o fluxo de integração completo."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = 'texto extraído'
        mock_get_reader.return_value = mock_reader

        mock_extractor = MagicMock()
        mock_extractor.extract_from_text.return_value = mock_successful_extraction
        mock_extractor_class.return_value = mock_extractor

        test_file = temp_dir / 'test.pdf'
        test_file.touch()

        result = extract_nfse_data(str(test_file), 'pdf')

        assert result == mock_successful_extraction
        mock_extractor_class.assert_called_once()
