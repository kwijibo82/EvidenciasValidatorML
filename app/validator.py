import pytesseract
import cv2
import numpy as np
import re
import os
import joblib
from datetime import date

MODELOS_PATH = os.path.join("app", "modelos")

# Carga segura de modelos
try:
    modelo_autor = joblib.load(os.path.join(MODELOS_PATH, "modelo_autor.pkl"))
    modelo_cliente = joblib.load(os.path.join(MODELOS_PATH, "modelo_cliente.pkl"))
    modelo_fecha = joblib.load(os.path.join(MODELOS_PATH, "modelo_fecha.pkl"))
    vectorizador = joblib.load(os.path.join(MODELOS_PATH, "vectorizer.pkl"))
except Exception as e:
    raise RuntimeError(f"[ERROR] Faltan modelos entrenados o están dañados: {e}")

def validar_evidencia(imagen_bytes, autor_esperado, cliente_proyecto, fecha_min, fecha_max):
    try:
        # Decodificación de la imagen
        img_array = np.frombuffer(imagen_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("No se pudo decodificar la imagen")

        # Preprocesamiento para OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, binaria = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        custom_config = r'--oem 3 --psm 6'
        texto = pytesseract.image_to_string(binaria, config=custom_config)
        print("[DEBUG OCR] Texto detectado:", texto)

        # Vectorizar el texto y realizar predicciones
        texto_procesado = vectorizador.transform([texto])
        autor_predicho = modelo_autor.predict(texto_procesado)[0]
        cliente_predicho = modelo_cliente.predict(texto_procesado)[0]
        fecha_predicha = modelo_fecha.predict(texto_procesado)[0]

        print(f"[DEBUG] Autor: {autor_predicho}, Cliente: {cliente_predicho}, Fecha: {fecha_predicha}")

        fecha_valida = comprobar_fecha(fecha_predicha, fecha_min, fecha_max)

        return {
            "autor_detectado": autor_predicho,
            "autor_valido": autor_esperado.lower() in autor_predicho.lower(),
            "cliente_detectado": cliente_predicho,
            "cliente_valido": cliente_proyecto.lower() in cliente_predicho.lower(),
            "fecha_detectada": fecha_predicha,
            "fecha_valida": fecha_valida
        }

    except Exception as e:
        print("[ERROR EN validar_evidencia()]:", e)
        raise

def comprobar_fecha(fecha_str: str, fecha_min: date, fecha_max: date) -> bool:
    if fecha_str == "No detectado":
        return False

    formatos = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d/%m"]
    for fmt in formatos:
        try:
            # Si es fecha tipo dd/mm, le añadimos el año por defecto
            if len(fecha_str) == 5:
                fecha_str = f"{fecha_str}/{fecha_min.year}"
            fecha = date.fromisoformat(fecha_str.replace("/", "-"))
            return fecha_min <= fecha <= fecha_max
        except Exception:
            continue
    return False
