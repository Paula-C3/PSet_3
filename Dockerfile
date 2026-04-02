FROM python:3.12-slim

WORKDIR /app

# Instalamos dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los archivos de requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "pydantic[email]" email-validator httpx uvicorn

# Copiamos todo el contenido del proyecto
COPY . .

# Importante: PYTHONPATH para que Python sepa donde esta la carpeta 'backend'
ENV PYTHONPATH=/app

EXPOSE 8000

# Ejecutamos la app desde el modulo principal
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]