from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.train_model import entrenar_modelo
from app.validator import validar_evidencia
from datetime import date
import os
import traceback

app = FastAPI(title="TrainerService - ML clásico")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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
    payload: str = Form(...),
):
    try:
        #Parsea el json que recibe como string
        data = json.loads(payload)
    
        autor_esperado = data.get("autor_esperado")
        cliente_proyecto = data.get("cliente_proyecto")
        fecha_min = data.get("fecha_min")
        fecha_max = data.get("fecha_max")
        primer_apellido = data.get("primer_apellido")
        segundo_apellido = data.get("segundo_apellido") 

        contenido = await file.read()

        # TODO: Remover debug
    
        print("[DEBUG]::: Autor esperado:", data["autor_esperado"])
        print("[DEBUG]::: Cliente proyecto:", data["cliente_proyecto"])
        print("[DEBUG]::: Fecha desde:", data["fecha_min"])
        print("[DEBUG]::: Fecha hasta:", data["fecha_max"])
        print("[DEBUG]::: Primer Apellido:", data["primer_apellido"])
        print("[DEBUG]::: Segundo Apellido:", data["segundo_apellido"])


        resultado = validar_evidencia(
            contenido,
            autor_esperado,
            cliente_proyecto,
            date.fromisoformat(fecha_min),
            date.fromisoformat(fecha_max)
        )

        return JSONResponse(
            content=resultado,
            status_code=200
        )
    
    except Exception as e:
        error_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print("[ERROR]", error_str)
        raise HTTPException(status_code=500, detail=f"Error en validación:\n{error_str}")
