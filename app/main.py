from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from app.train import entrenar_modelo
import os
import traceback
from fastapi import FastAPI, UploadFile, File, Form
from datetime import date


app = FastAPI(title="TrainerService - ML clásico")

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/train")
def entrenar():
    print("[DEBUG] Entrando al endpoint /train")
    try: 
        entrenar_modelo()
        return {"message": "Entrenamiento completado"}
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
async def validate_image(
    file: UploadFile = File(...),
    autor_esperado: str = Form(...),
    cliente_proyecto: str = Form(...),
    fecha_min: date = Form(...),
    fecha_max: date = Form(...)
):
    try:
        contenido = await file.read()
        resultado = validar_evidencia(
            contenido, autor_esperado, cliente_proyecto, fecha_min, fecha_max
        )
        return resultado
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error interno: {str(e)}"}
        )
