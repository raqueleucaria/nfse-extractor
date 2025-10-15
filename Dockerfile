FROM python:3.12

WORKDIR /code

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-por \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.1.3
RUN pip install "poetry==$POETRY_VERSION"

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock* /code/

RUN poetry install --no-interaction --no-ansi --no-root

COPY . /code/

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]