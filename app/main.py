from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.prediction_service import load_models, predict_fields
from app.services.ocr_service import extraer_texto_ocr
from app.services.trainer import entrenar_modelos
import pandas as pd
import os
import traceback
import io
from PIL import Image

# Inicializar FastAPI
app = FastAPI(title="Evidencias Validator ML")

# CORS settings
origins = ["http://localhost:4200", "http://127.0.0.1:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],º
    allow_headers=["*"],
)

# Cargar modelos al iniciar
vectorizer, model_autor, model_cliente, model_fecha, fecha_fija = load_models()

# Cargar autores y clientes conocidos
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
    return {"status": "ok"}


@app.post("/train")
def train():
    try:
        entrenar_modelos()
        return {"message": "Entrenamiento completado correctamente"}
    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento:\n{error_str}")


@app.get("/logs", response_class=PlainTextResponse)
def ver_logs():
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
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        texto_extraido = extraer_texto_ocr(image)

        # Realizar predicciones usando IA
        pred_autor, pred_cliente, pred_fecha = predict_fields(
            texto_extraido,
            vectorizer,
            model_autor,
            model_cliente,
            model_fecha
        )

        # Validaciones
        autor_valido = pred_autor.lower().strip() == autor.lower().strip()
        cliente_valido = pred_cliente.lower().strip() == cliente.lower().strip()
        fecha_valida = fecha_desde <= pred_fecha <= fecha_hasta

        return {
            "autor_detectado": pred_autor,
            "autor_valido": autor_valido,
            "cliente_detectado": pred_cliente,
            "cliente_valido": cliente_valido,
            "fecha_detectada": pred_fecha,
            "fecha_valida": fecha_valida
        }

    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        return JSONResponse(status_code=500, content={"error": error_str})
