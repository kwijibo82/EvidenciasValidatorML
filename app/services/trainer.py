import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from app.services.ocr_service import extraer_texto_ocr
from sklearn.model_selection import train_test_split

MODELOS_PATH = "app/modelos"
DATA_PATH = "data"
RAW_PATH = os.path.join(DATA_PATH, "raw")
LABELS_PATH = os.path.join(DATA_PATH, "labels.csv")
LOG_PATH = os.path.join(DATA_PATH, "errores_entrenamiento.log")

def entrenar_modelos():
    print("⏳ Iniciando procesamiento de evidencias...\n")

    if not os.path.exists(MODELOS_PATH):
        os.makedirs(MODELOS_PATH)

    evidencias = []
    autores = []
    clientes = []
    fechas = []

    errores = []

    df = pd.read_csv(LABELS_PATH)

    for idx, row in df.iterrows():
        filename = row['filename']
        autor = row['autor']
        cliente = row.get('cliente', None)
        fecha = row.get('fecha', None)

        ruta_imagen = os.path.join(RAW_PATH, filename)

        if not os.path.exists(ruta_imagen):
            error = f"[ERROR] {filename}: Archivo no encontrado: {ruta_imagen}"
            print(error)
            errores.append(error)
            continue

        try:
            texto_extraido = extraer_texto_ocr(ruta_imagen)
            evidencias.append(texto_extraido)
            autores.append(autor)
            clientes.append(cliente if cliente else "desconocido")
            fechas.append(str(fecha))
            print(f"[OK] {filename} procesado correctamente.")
        except Exception as e:
            error = f"[ERROR] {filename}: {str(e)}"
            print(error)
            errores.append(error)

    print("\n✅ OCR de evidencias completado.\n")

    # Guardar errores en log si los hay
    if errores:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            for err in errores:
                f.write(err + "\n")
    else:
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)

    if not evidencias:
        print("❌ No hay evidencias para entrenar.")
        return

    # Vectorización
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(evidencias)

    # Modelos
    model_autor = LogisticRegression(max_iter=1000)
    model_cliente = LogisticRegression(max_iter=1000)

    model_autor.fit(X, autores)
    model_cliente.fit(X, clientes)

    # Entrenamiento del modelo de fechas
    fechas_unicas = list(set(fechas))

    if len(fechas_unicas) == 1:
        # Si todas las fechas son iguales, guardar como constante
        fecha_fija = fechas_unicas[0]
        with open(os.path.join(MODELOS_PATH, "fecha_fija.txt"), "w", encoding="utf-8") as f:
            f.write(fecha_fija)
        print(f"✅ Guardada fecha fija {fecha_fija} (sin modelo de fecha).")
        model_fecha = None
    else:
        model_fecha = LogisticRegression(max_iter=1000)
        model_fecha.fit(X, fechas)
        joblib.dump(model_fecha, os.path.join(MODELOS_PATH, "modelo_fecha.pkl"))
        print("✅ Modelo de fecha entrenado correctamente.")

    # Guardar modelos
    joblib.dump(vectorizer, os.path.join(MODELOS_PATH, "vectorizer.pkl"))
    joblib.dump(model_autor, os.path.join(MODELOS_PATH, "modelo_autor.pkl"))
    joblib.dump(model_cliente, os.path.join(MODELOS_PATH, "modelo_cliente.pkl"))

    print("\n🏁 Proceso de entrenamiento finalizado.")
