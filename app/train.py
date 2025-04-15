import pandas as pd
import pytesseract
import cv2
import os
import re
import traceback
from app.utils import normalizar_nombre_archivo

def entrenar_modelo():
    errores = []
    log_path = "data/errores_entrenamiento.log"

    try:
        df = pd.read_csv("data/labels.csv", encoding="utf-8")
    except Exception as e:
        guardar_log(traceback.format_exc(), log_path)
        raise

    resultados = []

    for _, row in df.iterrows():
        try:
            original_filename = row["filename"]
            nombre_normalizado = normalizar_nombre_archivo(original_filename)

            ruta_base = os.path.join("data", "raw", os.path.splitext(nombre_normalizado)[0])
            ruta_normalizada = encontrar_archivo_existente(ruta_base)

            if not ruta_normalizada:
                raise FileNotFoundError(f"Imagen no encontrada: {ruta_base}[.png/.jpg/.jpeg]")

            texto = extraer_texto_ocr(ruta_normalizada)
            autor_detectado = extraer_autor(texto)
            fecha_detectada = extraer_fecha(texto)

            resultados.append({
                "filename": original_filename,
                "autor_real": row.get("autor", "Desconocido"),
                "autor_detectado": autor_detectado,
                "fecha_real": row.get("fecha", "Desconocido"),
                "fecha_detectada": fecha_detectada
            })

        except Exception as e:
            error_msg = f"[ERROR] Fallo procesando '{row['filename']}': {str(e)}"
            errores.append(error_msg)
            guardar_log(traceback.format_exc(), log_path)

    df_resultado = pd.DataFrame(resultados)
    os.makedirs("data", exist_ok=True)
    df_resultado.to_csv("data/resultado_entrenamiento.csv", index=False)
    print("[INFO] Resultado guardado en: data/resultado_entrenamiento.csv")

def encontrar_archivo_existente(ruta_base):
    extensiones = [".png", ".jpg", ".jpeg"]
    for ext in extensiones:
        ruta = ruta_base + ext
        if os.path.exists(ruta):
            return ruta
    return None

def guardar_log(texto, ruta):
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(texto + "\n")

def extraer_texto_ocr(ruta_imagen):
    print(f"[DEBUG] Procesando imagen: {ruta_imagen}")
    img = cv2.imread(ruta_imagen)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {ruta_imagen}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return pytesseract.image_to_string(thresh)

def extraer_autor(texto):
    patrones = [
        r"(?:Autor|Author|Committer|By):?\s*(.+)"
    ]
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "No detectado"

def extraer_fecha(texto):
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
