# Imagen base con Python y apt para instalar Tesseract
FROM python:3.11-slim

# Evita interacción durante instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instala Tesseract y los paquetes de idiomas necesarios
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    tesseract-ocr-cat \
    tesseract-ocr-glg \
    tesseract-ocr-eus \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    gcc \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (Render usa la variable $PORT)
EXPOSE 8000

# Comando de arranque del servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
