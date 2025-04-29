from datetime import datetime

def validar_evidencia(autor_predicho, cliente_predicho, fecha_predicha, datos_referencia):
    resultado = {
        "cliente_proyecto": False,
        "author": False,
        "fecha": False
    }

    # Validar autor
    if autor_predicho and datos_referencia["autor"]:
        resultado["author"] = autor_predicho.lower() == datos_referencia["autor"].lower()

    # Validar cliente
    if cliente_predicho and datos_referencia["cliente"]:
        resultado["cliente_proyecto"] = cliente_predicho.lower() == datos_referencia["cliente"].lower()

    # Validar fecha
    if fecha_predicha:
        try:
            fecha_dt = datetime.strptime(fecha_predicha, "%Y-%m-%d").date()
            fecha_desde = datetime.strptime(datos_referencia["fecha_desde"], "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(datos_referencia["fecha_hasta"], "%Y-%m-%d").date()

            resultado["fecha"] = fecha_desde <= fecha_dt <= fecha_hasta
        except Exception:
            resultado["fecha"] = False

    return resultado
