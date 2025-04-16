# 🧠 EvidenciasValidatorML

Servicio backend basado en FastAPI que utiliza OCR + Machine Learning para validar evidencias gráficas de commits de Git. A partir de capturas de pantalla, el sistema extrae texto con Tesseract y valida los siguientes parámetros entregados por el backend:

- 👤 **Autor del commit**
- 🏢 **Cliente o Proyecto**
- 📅 **Fecha (debe estar en un rango válido)**

## 📦 Estructura del Proyecto

```
.
├── app/
│   ├── main.py                # API FastAPI
│   ├── validator.py           # Lógica de validación
│   ├── train_model.py         # Entrenamiento de modelos
│   └── modelos/               # Modelos entrenados (.pkl)
├── data/
│   ├── labels.csv             # Etiquetas con autor y fecha
│   └── raw/                   # Capturas de pantalla (evidencias)
├── Dockerfile                 # Imagen para producción
├── requirements.txt           # Dependencias
└── README.md                  # Documentación
```

---

## 🚀 Instrucciones de Uso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu_usuario/evidencias-validator.git
cd evidencias-validator
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2.1 Después de ahí, es posible levantar el backend con un script en el archivo run.bat

```
.\run.bat
```

### 3. Estructura esperada del CSV, siendo el campo Apellido 2 opcional.
El archivo `data/labels.csv` debe tener este formato:

```csv
filename,autor,fecha
Nombre_Apellido1_Apellido2_Proyecto_Mes(mm)_Anio(YYYY).png,
...
```

Las imágenes deben estar en la carpeta `data/raw/`.

### 4. Entrenar el modelo
Puedes entrenar el modelo desde la API o manualmente:

#### Desde la API
```bash
curl -X POST http://localhost:8000/train
```

#### Desde consola
```bash
python -m app.entrenar_manual
```

### 5. Lanzar el servidor FastAPI
```bash
uvicorn app.main:app --reload
```

### 6. Acceder al Swagger
```
http://localhost:8000/docs
```

---

## 🧪 Endpoint de Validación

**POST /validate**

Campos del formulario:

- `file`: imagen
- `cliente_proyecto`: nombre del cliente
- `autor_esperado`: autor a validar
- `fecha_min`: fecha mínima permitida (YYYY-MM-DD)
- `fecha_max`: fecha máxima permitida (YYYY-MM-DD)

Respuesta esperada (JSON):
```json
{
  "autor_detectado": "John Doe",
  "autor_valido": true,
  "cliente_detectado": "Cliente",
  "cliente_valido": true,
  "fecha_detectada": "2025-01-07",
  "fecha_valida": true
}
```

---

## 🐳 Docker

### Build:
```bash
docker build -t evidencias-validator .
```

### Run:
```bash
docker run -p 8000:8000 evidencias-validator
```

---

## ⚠️ IMPORTANTE

- Tesseract debe estar instalado y accesible desde el entorno.
- La calidad del OCR mejora con imágenes nítidas y contrastadas.
- Actualmente se usa un modelo Naive Bayes; puede evolucionar a redes neuronales si se incrementa el dataset.

---

## 📬 Devs

Javier Mora && Albert Fondevila – Proyecto interno para la validación inteligente de evidencias de desarrollo.