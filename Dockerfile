FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Prepara archivos estáticos
RUN python manage.py collectstatic --noinput

# Descarga datos NLTK (evita hacerlo al iniciar)
RUN python -m nltk.downloader wordnet omw-1.4

ENV PYTHONUNBUFFERED 1

# Inicia el servidor con 1 worker y mayor timeout
CMD gunicorn EcoIntercambio_ProyectoIntegracion.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120
