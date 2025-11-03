# 1. Usa una imagen base de Python oficial, compatible con tus librerías
FROM python:3.12-slim

# 2. Instala dependencias de sistema (requeridas por PyMySQL, Scipy, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    # Dependencias generales (para librerías pesadas)
    && rm -rf /var/lib/apt/lists/*

# 3. Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copia el archivo requirements.txt e instala todas las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el resto del código
COPY . .

# 6. Prepara los archivos estáticos de Django para el servidor
RUN python manage.py collectstatic --noinput

# 7. Define el comando de inicio (lo que Azure ejecutará)
ENV PYTHONUNBUFFERED 1
# Usa el puerto 8000, estándar para Azure App Services con Docker
CMD gunicorn --bind 0.0.0.0:8000 --workers 4 Ecointercambio_ProyectoIntegracion.wsgi:application