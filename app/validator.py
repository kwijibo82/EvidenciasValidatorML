import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime
from app.utils import contiene_fecha_en_rango

def validar_evidencia(img_bytes, autor_esperado, cliente_proyecto, fecha_min, fecha_max):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("No se pudo procesar la imagen")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    texto = pytesseract.image_to_string(thresh)

    resultado = {
        "cliente_detectado": cliente_proyecto.lower() in texto.lower(),
        "autor_detectado": autor_esperado.lower() in texto.lower(),
        "fecha_detectada": contiene_fecha_en_rango(texto, fecha_min, fecha_max)
    }

    resultado["valido"] = all(resultado.values())
    return resultado
