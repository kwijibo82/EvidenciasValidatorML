import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from typing import Tuple

MODELOS_PATH = "app/modelos"

def load_models() -> Tuple[CountVectorizer, LogisticRegression, LogisticRegression, LogisticRegression | None, str | None]:
    """
    Carga los modelos y vectorizador desde disco. Si no hay modelo de fecha, devuelve None y la fecha fija.

    Returns:
        tuple: vectorizer, model_autor, model_cliente, model_fecha, fecha_fija
    """
    vectorizer = joblib.load(os.path.join(MODELOS_PATH, "vectorizer.pkl"))
    model_autor = joblib.load(os.path.join(MODELOS_PATH, "modelo_autor.pkl"))
    model_cliente = joblib.load(os.path.join(MODELOS_PATH, "modelo_cliente.pkl"))

    ruta_modelo_fecha = os.path.join(MODELOS_PATH, "modelo_fecha.pkl")
    ruta_fecha_fija = os.path.join(MODELOS_PATH, "fecha_fija.txt")

    if os.path.exists(ruta_modelo_fecha):
        model_fecha = joblib.load(ruta_modelo_fecha)
        fecha_fija = None
    elif os.path.exists(ruta_fecha_fija):
        with open(ruta_fecha_fija, "r", encoding="utf-8") as f:
            model_fecha = None
            fecha_fija = f.read().strip()
    else:
        model_fecha = None
        fecha_fija = None

    return vectorizer, model_autor, model_cliente, model_fecha, fecha_fija


def predict_fields(texto: str, vectorizer, model_autor, model_cliente, model_fecha) -> Tuple[str, str, str]:
    """
    Predice autor, cliente y fecha a partir del texto OCR.

    Args:
        texto (str): Texto extraído de la imagen.

    Returns:
        tuple: autor_predicho, cliente_predicho, fecha_predicha (como string)
    """
    X = vectorizer.transform([texto])
    autor_pred = model_autor.predict(X)[0]
    cliente_pred = model_cliente.predict(X)[0]

    if model_fecha:
        fecha_pred = model_fecha.predict(X)[0]
    else:
        # Si no hay modelo, devolver la fecha fija
        with open(os.path.join(MODELOS_PATH, "fecha_fija.txt"), "r", encoding="utf-8") as f:
            fecha_pred = f.read().strip()

    return autor_pred, cliente_pred, fecha_pred
