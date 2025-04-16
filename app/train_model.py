import pandas as pd
import os
import cv2
import pytesseract
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

DATA_FOLDER = "data"
RAW_FOLDER = os.path.join(DATA_FOLDER, "raw")
MODELOS_FOLDER = os.path.join("app", "modelos")
os.makedirs(MODELOS_FOLDER, exist_ok=True)

def extraer_texto_ocr(ruta_imagen):
    img = cv2.imread(ruta_imagen)
    if img is None:
        print(f"[WARN] No se pudo leer {ruta_imagen}")
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, binaria = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(binaria, config=config)

def entrenar_modelo():
    print("[INFO] Cargando etiquetas...")
    df = pd.read_csv(os.path.join(DATA_FOLDER, "labels.csv"), encoding="utf-8")

    print("[INFO] Extrayendo texto de las imágenes...")
    textos = []
    for filename in df["filename"]:
        ruta = os.path.join(RAW_FOLDER, filename)
        texto = extraer_texto_ocr(ruta)
        textos.append(texto)

    df["texto"] = textos

    print("[INFO] Vectorizando texto...")
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df["texto"])

    print("[INFO] Entrenando modelos...")
    modelo_autor = MultinomialNB().fit(X, df["autor"])
    modelo_cliente = MultinomialNB().fit(
        X, df["filename"].str.extract(r'_(\w+)_01_2025')[0].fillna("Desconocido")
    )
    modelo_fecha = MultinomialNB().fit(X, df["fecha"])

    print("[INFO] Guardando modelos...")
    joblib.dump(modelo_autor, os.path.join(MODELOS_FOLDER, "modelo_autor.pkl"))
    joblib.dump(modelo_cliente, os.path.join(MODELOS_FOLDER, "modelo_cliente.pkl"))
    joblib.dump(modelo_fecha, os.path.join(MODELOS_FOLDER, "modelo_fecha.pkl"))
    joblib.dump(vectorizer, os.path.join(MODELOS_FOLDER, "vectorizer.pkl"))

    print("[✅] Entrenamiento completado correctamente.")
