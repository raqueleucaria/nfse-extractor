import sys
import json
from pathlib import Path
from extractor.data_extractor import extract_nfse_data


def main():
    if len(sys.argv) < 2:
        print("Uso: python extract_cli.py <caminho_arquivo>")
        print("\nExemplos:")
        print("  python extract_cli.py test_files/NFSe_ficticia_layout_completo.pdf")
        print("  python extract_cli.py test_files/nfse_test.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        file_type = sys.argv[2]
    else:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            file_type = 'pdf'
        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            file_type = 'image'
        else:
            print(f"Erro: Extensão não reconhecida '{ext}'. Especifique o tipo manualmente.")
            sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"Erro: Arquivo não encontrado: {file_path}")
        sys.exit(1)
    
    # print(f"Processando {file_type.upper()}: {file_path}")
    
    try:
        result = extract_nfse_data(file_path, file_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

