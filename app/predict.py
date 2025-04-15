import pytesseract
import cv2
import numpy as np
import joblib
import os

modelo_path = "models/modelo_entrenado.pkl"

def predecir_desde_imagen(image_bytes: bytes) -> dict:
    if not os.path.exists(modelo_path):
        return {"error": "Modelo no entrenado. Usa /train primero."}

    texto_extraido = ocr_desde_bytes(image_bytes)
    modelo = joblib.load(modelo_path)
    ide_predicho = modelo.predict([texto_extraido])[0]

    return {
        "ide": ide_predicho,
        "autor": "por detectar",
        "cliente": "por detectar",
        "fecha": "por detectar"
    }

def ocr_desde_bytes(image_bytes: bytes) -> str:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    texto = pytesseract.image_to_string(thresh)
    return texto
