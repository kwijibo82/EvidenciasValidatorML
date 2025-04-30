# Imagen base con Python y apt para instalar Tesseract
FROM python:3.11-slim

# Evita interacción en instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instala Tesseract y dependencias de sistema
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev poppler-utils gcc build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposición del puerto (Render usa $PORT env var)
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
