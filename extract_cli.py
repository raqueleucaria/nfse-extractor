import argparse
import json
import logging
import sys
from pathlib import Path

from extractor.data_extractor import ExtractorError, extract_nfse_data


def main():
    SUPPORTED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'}

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        stream=sys.stderr,
    )

    parser = argparse.ArgumentParser(
        description='Extrai CNPJ e Razão Social de documentos fiscais (NFSe).',
        epilog='Exemplo: python extract_cli.py '
        '"test_files/NFSe_ficticia_layout_completo.pdf"',
    )
    parser.add_argument(
        'filepath',
        type=str,
        help='Caminho completo para o arquivo PDF ou de imagem.',
    )

    args = parser.parse_args()

    file_path_str = args.filepath
    file_path = Path(file_path_str)

    if not file_path.exists():
        logging.error(f'Arquivo não encontrado: {file_path_str}')
        sys.exit(1)

    file_extension = file_path.suffix.lower().lstrip('.')
    if file_extension == 'pdf':
        file_type = 'pdf'
    elif file_extension in SUPPORTED_IMAGE_EXTENSIONS:
        file_type = 'image'
    else:
        logging.error(f"Extensão de arquivo não suportada: '{file_extension}'")
        sys.exit(1)

    logging.info(f'Processando {file_type.upper()}: {file_path_str}')

    try:
        result = extract_nfse_data(file_path_str, file_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except ExtractorError as e:
        logging.error(f'Falha na extração: {e}')
        sys.exit(1)
    except Exception as e:
        logging.critical(f'Um erro inesperado e fatal ocorreu: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
