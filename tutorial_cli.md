## ⚡ Como rodar via terminal (CLI) com Poetry ou Docker

Você pode extrair informações de NFSe diretamente pelo terminal usando o script `extract_cli.py`.

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation) ou Docker
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (se optar pelo poetry)

### Instalação com Poetry

```bash
git clone https://github.com/raqueleucaria/nfse-extractor.git
cd nfse-extractor
poetry install
```

### Execução com Poetry

Para extrair dados de um arquivo PDF ou imagem, execute:

```bash
poetry run python extract_cli.py caminho/para/seu/arquivo.pdf
```

Exemplo:

```bash
poetry run python extract_cli.py test_files/NFSe_ficticia_layout_completo.pdf
```

O resultado será exibido em formato JSON no terminal.

---

### Execução com Docker

Se preferir usar Docker, execute:

```bash
docker compose run web python extract_cli.py caminho/para/seu/arquivo.pdf
```

Exemplo:

```bash
docker compose run web python extract_cli.py test_files/NFSe_ficticia_layout_completo.pdf
```

O resultado também será exibido em formato JSON no terminal.