import pytesseract
import cv2
import numpy as np
import re
from datetime import date, datetime


def validar_evidencia(imagen_bytes, autor_esperado, cliente_proyecto, fecha_min, fecha_max):
    img_array = np.frombuffer(imagen_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo decodificar la imagen")

    # Preprocesamiento más robusto
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

    custom_config = r'--oem 3 --psm 6'
    texto = pytesseract.image_to_string(gray, config=custom_config)

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
        r"(?:Autor|Author|Committer|By|Committed by):?\s*(.+)",
        r"by\s+([\w .<>@]+)",
        r"committed\s+by\s+([\w .<>@]+)"
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
        r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b",  # dd/mm/yyyy o dd-mm-yyyy
        r"\b(\d{4})[/-](\d{2})[/-](\d{2})\b",  # yyyy-mm-dd o yyyy/mm/dd
        r"\b(\d{2})[/-](\d{2})\b",             # dd/mm
    ]
    for patron in patrones:
        matches = re.findall(patron, texto)
        for match in matches:
            if len(match) == 3:
                dia, mes, anio = match if int(match[0]) <= 31 else (match[2], match[1], match[0])
                if 1 <= int(dia) <= 31 and 1 <= int(mes) <= 12:
                    return f"{dia.zfill(2)}/{mes.zfill(2)}/{anio}"
            elif len(match) == 2:
                dia, mes = match
                if 1 <= int(dia) <= 31 and 1 <= int(mes) <= 12:
                    return f"{dia.zfill(2)}/{mes.zfill(2)}"
    return "No detectado"

def comprobar_fecha(fecha_str: str, fecha_min: date, fecha_max: date) -> bool:
    if fecha_str == "No detectado":
        return False

    formatos = ["%d/%m/%Y", "%Y/%m/%d", "%d/%m"]
    for fmt in formatos:
        try:
            if fmt == "%d/%m":
                fecha_str += f"/{fecha_min.year}"
            fecha = datetime.strptime(fecha_str, fmt).date()
            return fecha_min <= fecha <= fecha_max
        except ValueError:
            continue
    return False