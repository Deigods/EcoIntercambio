# 1. Imagen base
FROM python:3.12-slim

# 2. Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo
WORKDIR /app
ENV PYTHONPATH=/app

# 4. Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el código
COPY . .

# 6. Recolecta archivos estáticos
RUN python manage.py collectstatic --noinput

# 7. Expone puerto (opcional)
EXPOSE 8000

# 8. Arranca con Daphne (ASGI compatible)
ENV PYTHONUNBUFFERED=1
CMD ["daphne", "-b", "0.0.0.0", "-p", "$PORT", "EcoIntercambio_ProyectoIntegracion.asgi:application"]