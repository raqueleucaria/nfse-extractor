import re
from pathlib import Path
from typing import Dict, Optional

import pdfplumber
import pytesseract
from PIL import Image


class ExtractorError(Exception):
    """Exceção base para erros do extrator"""

    pass


class FileNotFoundError(ExtractorError):
    """Arquivo não encontrado"""

    pass


class UnsupportedFileTypeError(ExtractorError):
    """Tipo de arquivo não suportado"""

    pass


class ProcessingError(ExtractorError):
    """Erro durante o processamento do arquivo"""

    pass


class ExtractorConfig:
    """Configurações para o extrator de dados NFSe"""

    CNPJ_PRESTADOR = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
    RAZAO_SOCIAL_PRESTADOR = r'Razão Social:\s*(.+?)(?:\n|$)'
    PRESTADOR_START = r'Dados do Prestador'
    PRESTADOR_END = r'Dados do Tomador'
    OCR_LANG = 'por'


class Reader:
    """Classe base para leitores de arquivo"""

    @staticmethod
    def read(file_path: str) -> str:
        raise NotImplementedError('O método read() deve ser implementado')


class PDFReader(Reader):
    """Leitor para arquivos PDF usando pdfplumber"""

    @staticmethod
    def read(file_path: str) -> str:
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(
                    f'Arquivo PDF não encontrado: {file_path}'
                )

            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    raise ProcessingError('PDF não contém páginas válidas')

                full_text = '\n'.join(
                    page.extract_text()
                    for page in pdf.pages
                    if page.extract_text()
                )

                if not full_text.strip():
                    raise ProcessingError('Não foi possível extrair texto do PDF')

                return full_text

        except pdfplumber.PDFSyntaxError as e:
            raise ProcessingError(
                f'Arquivo PDF corrompido ou com sintaxe inválida: {e}'
            )
        except PermissionError:
            raise ProcessingError(
                f'Sem permissão para ler o arquivo: {file_path}'
            )
        except Exception as e:
            if isinstance(e, ExtractorError):
                raise
            raise ProcessingError(f'Erro inesperado ao processar o PDF: {e}')


class ImageReader(Reader):
    """Leitor para arquivos de imagem usando Tesseract OCR"""

    @staticmethod
    def read(file_path: str) -> str:
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(
                    f'Arquivo de imagem não encontrado: {file_path}'
                )

            image = Image.open(file_path)
            image.verify()
            image = Image.open(file_path)

            extracted_text = pytesseract.image_to_string(
                image, lang=ExtractorConfig.OCR_LANG
            )

            if not extracted_text.strip():
                raise ProcessingError('Não foi possível extrair texto da imagem')

            return extracted_text
        except pytesseract.TesseractNotFoundError:
            raise ProcessingError(
                'Tesseract OCR não instalado ou presente no PATH do sistema.'
            )
        except PermissionError:
            raise ProcessingError(
                f'Sem permissão para ler o arquivo: {file_path}'
            )
        except Exception as e:
            if isinstance(e, ExtractorError):
                raise
            raise ProcessingError(
                f'Arquivo não é uma imagem válida ou ocorreu um erro no OCR: {e}'
            )


class NFSeExtractor:
    """Extrator de dados de NFSe a partir de uma string de texto"""

    def __init__(self, config: ExtractorConfig = None):
        self.config = config or ExtractorConfig()

    def extract_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai CNPJ e Razão Social do texto da NFSe.
        Este é o método público principal da classe.
        """
        prestador_section = self._isolate_prestador_section(text)

        return {
            'cnpj_prestador': self._extract_cnpj(prestador_section),
            'nome_prestador': self._extract_razao_social(prestador_section),
        }

    def _isolate_prestador_section(self, text: str) -> str:
        """Isola a seção do prestador para uma busca mais precisa."""
        start_match = re.search(self.config.PRESTADOR_START, text, re.IGNORECASE)
        if not start_match:
            return text

        text_after_start = text[start_match.end() :]
        end_match = re.search(
            self.config.PRESTADOR_END, text_after_start, re.IGNORECASE
        )

        if end_match:
            return text_after_start[: end_match.start()]

        return text_after_start

    def _extract_cnpj(self, text: str) -> Optional[str]:
        """Extrai o primeiro CNPJ encontrado no texto fornecido."""
        match = re.search(self.config.CNPJ_PRESTADOR, text)
        return match.group(0) if match else None

    def _extract_razao_social(self, text: str) -> Optional[str]:
        """Extrai a Razão Social do texto fornecido."""
        match = re.search(self.config.RAZAO_SOCIAL_PRESTADOR, text)
        return match.group(1).strip() if match else None


def get_reader(file_type: str) -> Reader:
    """Factory que retorna o leitor apropriado para o tipo de arquivo."""
    file_type_lower = file_type.lower()

    if file_type_lower == 'pdf':
        return PDFReader()
    if file_type_lower == 'image':
        return ImageReader()
    raise UnsupportedFileTypeError(f'Tipo de arquivo não suportado: {file_type}')


def extract_nfse_data(
    file_path_str: str, file_type: str
) -> Dict[str, Optional[str]]:
    """
    Orquestra o processo de extração de dados de um arquivo NFSe.
    """
    file_path = Path(file_path_str)
    if not file_path.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {file_path_str}')

    reader = get_reader(file_type)
    raw_text = reader.read(str(file_path))
    data_extractor = NFSeExtractor()
    return data_extractor.extract_from_text(raw_text)
