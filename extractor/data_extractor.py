import re
import pdfplumber
import pytesseract
from PIL import Image
from typing import Dict, Optional


class NFSeExtractor:
    """Classe para extração de CNPJ e Razão Social de documentos NFSe"""
    
    # XX.XXX.XXX/XXXX-XX
    CNPJ_PATTERN = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
    
    def __init__(self):
        self.text = ""
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Optional[str]]:
        """Extrai todo o texto do PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                self.text = full_text
                return self._extract_data()
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    def extract_from_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """Extrai todo o texto da imagem usando OCR para conversão."""
        try:
            image = Image.open(image_path)
            self.text = pytesseract.image_to_string(image, lang='por')
            return self._extract_data()
        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")
    
    def _extract_data(self) -> Dict[str, Optional[str]]:
        """Extrai CNPJ e Razão Social do texto extraído (normalizando e filtrando)."""
        
        normalized_text = re.sub(r'\s+', ' ', self.text)
        
        cnpj_prestador = self._extract_cnpj_prestador(normalized_text)
        nome_prestador = self._extract_razao_social(normalized_text)
        
        return {
            "cnpj_prestador": cnpj_prestador,
            "nome_prestador": nome_prestador
        }
    
    def _extract_cnpj_prestador(self, text: str) -> Optional[str]:
        """Extrai o primeiro CNPJ encontrado após a seção "Dados do Prestador de Serviços"."""

        cnpjs = re.findall(self.CNPJ_PATTERN, text)
        
        if not cnpjs:
            return None
        
        prestador_match = re.search(
            r'Dados do Prestador de Servi[çc]os',
            text,
            re.IGNORECASE
        )
        
        if prestador_match:
            text_after_prestador = text[prestador_match.end():]
            cnpj_match = re.search(self.CNPJ_PATTERN, text_after_prestador)
            
            if cnpj_match: return cnpj_match.group(0)
        
        return cnpjs[0] if cnpjs else None
    
    def _extract_razao_social(self, text: str) -> Optional[str]:
        """Extrai a Razão Social buscando padrões como "Razão Social: NOME" na seção do prestador."""
        
        prestador_match = re.search(
            r'Dados do Prestador de Servi[çc]os',
            text,
            re.IGNORECASE
        )
        
        if not prestador_match: return None
        
        text_after_prestador = text[prestador_match.end():]
        
        # Limitar a busca
        next_section_match = re.search(
            r'Dados do Tomador|Discrimina[çc][ãa]o dos Servi[çc]os',
            text_after_prestador,
            re.IGNORECASE
        )
        
        if next_section_match: text_after_prestador = text_after_prestador[:next_section_match.start()]
        
        razao_match = re.search(
            r'Raz[ãa]o Social:?\s*([A-ZÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜ\s\.]+?)(?:\s+Nome Fantasia|\s+CNPJ|\s+Inscri[çc][ãa]o)',
            text_after_prestador,
            re.IGNORECASE
        )
        
        if razao_match:
            razao_social = razao_match.group(1).strip()
            razao_social = re.sub(r'\s+', ' ', razao_social)
            return razao_social
        
        return None
    
    def get_raw_text(self) -> str:
        return self.text


def extract_nfse_data(file_path: str, file_type: str = 'pdf') -> Dict[str, Optional[str]]:
    """Extrai o tipo de arquivo e chama o método apropriado."""
    
    extractor = NFSeExtractor()
    
    if file_type.lower() == 'pdf':
        return extractor.extract_from_pdf(file_path)
    elif file_type.lower() in ['image', 'img', 'png', 'jpg', 'jpeg']:
        return extractor.extract_from_image(file_path)
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {file_type}")

