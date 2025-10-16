# NFSE-extractor

Extraia informações de Notas Fiscais de Serviço (NFSe) de arquivos PDF ou imagem de forma rápida e intuitiva.

![Demonstração NFSe Extractor](docs/nfse.gif)


## 🚀 Projeto

- [GitHub Project](https://github.com/users/raqueleucaria/projects/10?pane=info)
- [Backlog e requisitos](docs/backlog.md)


## 📝 Funcionalidades

- Upload de arquivos PDF, PNG, JPG
- Extração automática de CNPJ e Razão Social do prestador
- Visualização dos dados extraídos em JSON
- Interface intuitiva e responsiva
- Execução via terminal usando o script `extract_cli.py`


## ⚡ Como rodar localmente

É possível executar com o frontend Django ou apenas no terminal usando o script `extract_cli.py`.  
Para mais informações sobre o uso via CLI, acesse o [tutorial CLI](docs/tutorial_cli.md).

### Pré-requisitos

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation) ou Docker
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (se optar pelo poetry)

### Instalação com Poetry

```bash
git clone https://github.com/raqueleucaria/nfse-extractor.git
cd nfse-extractor
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Acesse [http://localhost:8000](http://localhost:8000) no navegador.

### Instalação com Docker

```bash
git clone https://github.com/raqueleucaria/nfse-extractor.git
cd nfse-extractor
docker compose up --build
```

Acesse [http://localhost:8000](http://localhost:8000) no navegador.


## ✅ Testes Automatizados

O projeto possui testes automatizados para garantir a correta extração dos dados das notas fiscais.  
Foram criados testes tanto para as views quanto para o backend presente em `extractor/data_extractor.py`, cobrindo cenários de extração de CNPJ, Razão Social e tratamento de arquivos.

### Como rodar os testes

**Com Poetry:**
```bash
poetry run pytest --cov=. --cov-report=term-missing
```

**Com Docker:**
```bash
docker compose run web poetry run pytest --cov=. --cov-report=term-missing
```

Os resultados dos testes e o relatório de cobertura serão exibidos no terminal, permitindo validar rapidamente se as funcionalidades principais estão funcionando conforme esperado.


## 📂 Arquivos de exemplo para teste

Para facilitar os testes, o projeto inclui arquivos de exemplo em:

- [`docs/arquivos`](docs/arquivos/)  
  Exemplos e documentação adicional.

- [`test_files/`](test_files/)  
  Arquivos de NFSe fictícios para testar a extração.

Utilize esses arquivos para validar a extração de dados tanto pela interface web quanto pelo CLI.
