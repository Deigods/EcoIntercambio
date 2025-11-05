# 1. Usa una imagen base de Python oficial, compatible con tus librerías
FROM python:3.12-slim

# 2. Instala dependencias de sistema (requeridas por PyMySQL, Scipy, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# ** LÍNEA CRÍTICA 1 **: Asegura la ruta base
ENV PYTHONPATH=/app

# 4. Copia el archivo requirements.txt e instala todas las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el resto del código
COPY . .

# 6. Prepara los archivos estáticos de Django para el servidor
RUN python manage.py collectstatic --noinput

# 7. Define el comando de inicio
ENV PYTHONUNBUFFERED 1
# ¡CRÍTICO! Corregimos la capitalización: EcoIntercambio_ProyectoIntegracion
CMD gunicorn EcoIntercambio_ProyectoIntegracion.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT