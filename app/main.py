from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.prediction_service import load_models, predict_fields
from app.services.ocr_service import extraer_texto_ocr
from app.services.trainer import entrenar_modelos
from app.services.validator_service import validar_evidencia
import pandas as pd
import os
import traceback
import io
from PIL import Image

# Inicializar FastAPI
app = FastAPI(title="Evidencias Validator ML")

# Configurar CORS (ajusta los orígenes según tu frontend)
origins = ["http://localhost:4200", "http://127.0.0.1:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelos al iniciar la app
vectorizer, model_autor, model_cliente, model_fecha, _ = load_models()

# Cargar autores y clientes conocidos (opcional para ver en Swagger)
labels_path = "data/labels.csv"
if os.path.exists(labels_path):
    labels_df = pd.read_csv(labels_path)
    autores_conocidos = labels_df['autor'].dropna().unique().tolist()
    clientes_conocidos = labels_df['cliente'].dropna().unique().tolist()
else:
    autores_conocidos = []
    clientes_conocidos = []


@app.get("/status")
def status():
    """Check de estado simple."""
    return {"status": "ok"}


@app.post("/train")
def train():
    """Lanza el proceso de entrenamiento."""
    try:
        entrenar_modelos()
        return {"message": "Entrenamiento completado correctamente"}
    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento:\n{error_str}")


@app.get("/logs", response_class=PlainTextResponse)
def ver_logs():
    """Consulta el log de errores del último entrenamiento."""
    ruta_log = "data/errores_entrenamiento.log"
    if not os.path.exists(ruta_log):
        raise HTTPException(status_code=404, detail="No se ha generado ningún log de errores todavía.")
    with open(ruta_log, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/validate")
async def validate(
    file: UploadFile = File(...),
    autor: str = Form(...),
    cliente: str = Form(...),
    fecha_desde: str = Form(...),
    fecha_hasta: str = Form(...)
):
    """
    Valida una evidencia subida:
    - Compara autor OCR vs autor esperado.
    - Compara cliente OCR vs cliente esperado.
    - Valida que la fecha OCR esté en el rango dado.
    """
    try:
        # Leer la imagen recibida
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # OCR para extraer texto
        texto_extraido = extraer_texto_ocr(image)

        # IA: predecir autor, cliente y fecha
        pred_autor, pred_cliente, pred_fecha = predict_fields(
            texto_extraido,
            vectorizer,
            model_autor,
            model_cliente,
            model_fecha
        )

        # Validación usando la función centralizada
        datos_referencia = {
            "autor": autor,
            "cliente": cliente,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }

        resultado_validacion = validar_evidencia(pred_autor, pred_cliente, pred_fecha, datos_referencia)

        # Respuesta final
        return {
            "autor_detectado": pred_autor,
            "autor_valido": resultado_validacion["autor_valido"],
            "cliente_detectado": pred_cliente,
            "cliente_valido": resultado_validacion["cliente_valido"],
            "fecha_detectada": pred_fecha,
            "fecha_valida": resultado_validacion["fecha_valida"]
        }

    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        return JSONResponse(status_code=500, content={"error": error_str})
