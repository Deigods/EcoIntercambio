# Imagen base ligera
FROM python:3.12-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app
ENV PYTHONPATH=/app

# Copia e instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto
COPY . .

# Recolecta estáticos y migra la base de datos (Render lo hace automáticamente, pero se puede dejar)
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

# Descarga datos opcionales de NLTK
RUN python -m nltk.downloader wordnet omw-1.4

# Variables de entorno
ENV PYTHONUNBUFFERED=1

# Usa Daphne (servidor oficial de Django Channels)
CMD daphne -b 0.0.0.0 -p ${PORT:-8000} EcoIntercambio_ProyectoIntegracion.asgi:application
