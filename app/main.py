from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from app.train_model import entrenar_modelo
from app.validator import validar_evidencia
from datetime import date
import os
import traceback

app = FastAPI(title="TrainerService - ML clásico")

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
        print("[ERROR]", error_str)
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
    cliente_proyecto: str = Form(...),
    autor_esperado: str = Form(...),
    fecha_min: date = Form(...),
    fecha_max: date = Form(...)
):
    try:
        contenido = await file.read()
        resultado = validar_evidencia(
            contenido, autor_esperado, cliente_proyecto, fecha_min, fecha_max
        )
        print("[DEBUG] Resultado:", resultado)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar evidencia: {str(e)}")
