# Imagen base
FROM python:3.12-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app
ENV PYTHONPATH=/app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Archivos estáticos
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

# Descargar datos NLTK (opcional)
RUN python -m nltk.downloader wordnet omw-1.4

# Variables de entorno
ENV PYTHONUNBUFFERED 1

# Servidor Gunicorn con Uvicorn
CMD gunicorn EcoIntercambio_ProyectoIntegracion.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120
