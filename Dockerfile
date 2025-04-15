FROM python:3.10-slim

# Instalar dependencias del sistema (incluye tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Crear y usar directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Puerto expuesto
EXPOSE 8000

# Comando por defecto: iniciar Uvicorn (Render también lo usará)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
