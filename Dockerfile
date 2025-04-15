FROM python:3.10

# Instalar tesseract y dependencias
RUN apt-get update && apt-get install -y tesseract-ocr libgl1

# Crear directorio de trabajo
WORKDIR /app

# Copiar el proyecto
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que usará Uvicorn
EXPOSE 10000

# Comando para iniciar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
