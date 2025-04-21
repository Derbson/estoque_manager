FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Instala dependências do SO necessárias para psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 2) Copia só o arquivo de dependências e instala
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 3) Copia o restante do código
COPY . /app

RUN python manage.py collectstatic --noinput


EXPOSE 8000

CMD ["bash", "-c", "\
  until nc -z db 5432; do echo 'Waiting for Postgres...'; sleep 1; done && \
  python manage.py migrate && \
  gunicorn core.wsgi:application --bind 0.0.0.0:8000\
"]
