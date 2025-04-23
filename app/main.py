from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.train_model import entrenar_modelo
from app.validator import validar_evidencia
from datetime import date
import traceback
import os

app = FastAPI(title="TrainerService - ML clásico")

# CORS settings
origins = ["http://localhost:4200", "http://127.0.0.1:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/train")
def entrenar():
    try:
        entrenar_modelo()
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
    autor_esperado: str = Form(...),
    cliente_proyecto: str = Form(...),
    fecha_min: str = Form(...),
    fecha_max: str = Form(...),
    primer_apellido: str = Form(...),
    segundo_apellido: str = Form(None),
):
    try:
        contenido = await file.read()
        print(f"[DEBUG]::: Archivo recibido - nombre: {file.filename}, tamaño: {len(contenido)} bytes")
        resultado = validar_evidencia(
            contenido,
            autor_esperado,
            cliente_proyecto,
            date.fromisoformat(fecha_min),
            date.fromisoformat(fecha_max),
        )
        return JSONResponse(content=resultado, status_code=200)
    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        raise HTTPException(status_code=500, detail=f"Error en validación:\n{error_str}")
