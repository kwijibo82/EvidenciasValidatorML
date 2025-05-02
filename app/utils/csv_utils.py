import pandas as pd
import os

LABELS_PATH = "data/labels.csv"

def autor_existe(autor: str) -> bool:
    """
    Comprueba si un autor ya está en el CSV.
    """
    if not os.path.exists(LABELS_PATH):
        return False
    df = pd.read_csv(LABELS_PATH)
    autores = df['autor'].dropna().str.lower().tolist()
    return autor.lower() in autores


def agregar_nueva_evidencia(nueva_fila: dict):
    """
    Añade una nueva evidencia al CSV (append).
    """
    if not os.path.exists(LABELS_PATH):
        # Crear un nuevo CSV si no existe
        df = pd.DataFrame([nueva_fila])
        df.to_csv(LABELS_PATH, index=False)
    else:
        df = pd.read_csv(LABELS_PATH)
        df = df.append(nueva_fila, ignore_index=True)
        df.to_csv(LABELS_PATH, index=False)
