import pytesseract
import re
from datetime import datetime
import cv2
import numpy as np
import re

def extraer_texto(imagen_bytes: bytes) -> str:
    image = cv2.imdecode(np.frombuffer(imagen_bytes, np.uint8), cv2.IMREAD_COLOR)
    texto = pytesseract.image_to_string(image)
    return texto

def contiene_fecha_valida(texto: str, fecha_min, fecha_max) -> str:
    posibles_fechas = re.findall(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", texto)
    for fecha in posibles_fechas:
        try:
            f = datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            try:
                f = datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                continue
        if fecha_min <= f.date() <= fecha_max:
            return fecha
    return "No detectado"

def normalizar_nombre_archivo(nombre: str) -> str:
    # Separar nombre base y extensión
    base, extension = os.path.splitext(nombre)
    
    # Normalizar caracteres (quita acentos)
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    
    # Reemplazar espacios y caracteres no deseados
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"\s+", "_", base)

    # Recomponer nombre y extensión
    return f"{base.lower()}{extension.lower()}"

def contiene_fecha_en_rango(texto, fecha_min, fecha_max):
    patrones = [
        r"\d{4}[-/]\d{2}[-/]\d{2}",
        r"\d{2}[-/]\d{2}[-/]\d{4}",
        r"\d{2}/\d{2}"
    ]

    for patron in patrones:
        coincidencias = re.findall(patron, texto)
        for fecha_str in coincidencias:
            for formato in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d/%m"):
                try:
                    fecha = datetime.strptime(fecha_str, formato).date()
                    if fecha_min <= fecha <= fecha_max:
                        return True
                except:
                    continue
    return False
