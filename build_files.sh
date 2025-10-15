pip install poetry
poetry config virtualenvs.create false
poetry install --no-dev

python manage.py collectstatic --noinput

chmod -R 755 staticfiles