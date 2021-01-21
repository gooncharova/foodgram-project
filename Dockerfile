FROM python:3.8.5
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD bash -c "python3 manage.py collectstatic --no-input && gunicorn foodgram_project.wsgi:application --bind 0.0.0.0:8000"