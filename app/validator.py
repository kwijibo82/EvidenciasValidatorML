import pytesseract
import cv2
import numpy as np
import re
from datetime import date

def validar_evidencia(imagen_bytes, autor_esperado, cliente_proyecto, fecha_min, fecha_max):
    img_array = np.frombuffer(imagen_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo decodificar la imagen")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    texto = pytesseract.image_to_string(binaria)

    autor_detectado = extraer_autor(texto)
    cliente_detectado = extraer_cliente(texto, cliente_proyecto)
    fecha_detectada = extraer_fecha(texto)
    fecha_valida = comprobar_fecha(fecha_detectada, fecha_min, fecha_max)

    return {
        "autor_detectado": autor_detectado,
        "autor_valido": autor_esperado.lower() in autor_detectado.lower(),
        "cliente_detectado": cliente_detectado,
        "cliente_valido": cliente_proyecto.lower() in cliente_detectado.lower(),
        "fecha_detectada": fecha_detectada,
        "fecha_valida": fecha_valida
    }


def extraer_autor(texto: str) -> str:
    patrones = [
        r"(?:Autor|Author|Committer|By):?\s*(.+)",
        r"by\s+(.+)",
        r"commit\s+by\s+(.+)"
    ]
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "No detectado"


def extraer_cliente(texto: str, cliente: str) -> str:
    if cliente.lower() in texto.lower():
        return cliente
    return "No detectado"


def extraer_fecha(texto: str) -> str:
    patrones = [
        r"\d{4}[-/]\d{2}[-/]\d{2}",
        r"\d{2}[-/]\d{2}[-/]\d{4}",
        r"\d{2}/\d{2}"
    ]
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            return match.group(0)
    return "No detectado"


def comprobar_fecha(fecha_str: str, fecha_min: date, fecha_max: date) -> bool:
    if fecha_str == "No detectado":
        return False

    formatos = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d/%m"]
    for fmt in formatos:
        try:
            if len(fecha_str) == 5:  # dd/mm
                fecha_str = f"{fecha_str}/{fecha_min.year}"
            fecha = date.fromisoformat(fecha_str.replace("/", "-"))
            return fecha_min <= fecha <= fecha_max
        except Exception:
            continue
    return False
