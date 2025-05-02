from datetime import datetime

def validar_evidencia(autor_predicho, cliente_predicho, fecha_predicha, datos_referencia):
    """
    Valida la evidencia completa:
    - Autor detectado vs autor esperado.
    - Cliente detectado vs cliente esperado.
    - Fecha detectada dentro del rango esperado.

    Args:
        autor_predicho (str): Autor detectado por OCR/ML.
        cliente_predicho (str): Cliente detectado.
        fecha_predicha (str): Fecha detectada (formato string).
        datos_referencia (dict): Diccionario con 'autor', 'cliente', 'fecha_desde', 'fecha_hasta'.

    Returns:
        dict: Resultado de las validaciones.
    """
    resultado = {
        "autor_valido": False,
        "cliente_valido": False,
        "fecha_valida": False
    }

    # Validar autor
    if autor_predicho and datos_referencia["autor"]:
        resultado["autor_valido"] = autor_predicho.strip().lower() == datos_referencia["autor"].strip().lower()

    # Validar cliente
    if cliente_predicho and datos_referencia["cliente"]:
        resultado["cliente_valido"] = cliente_predicho.strip().lower() == datos_referencia["cliente"].strip().lower()

    # Validar fecha OCR dentro de rango dinámico
    if fecha_predicha:
        try:
            # Normaliza la fecha detectada a formato datetime
            fecha_dt = None
            fecha_predicha = fecha_predicha.strip()

            # Limpiar y detectar formatos más flexibles
            fecha_numerica = ''.join(c for c in fecha_predicha if c.isdigit())

            if len(fecha_numerica) == 8:
                # Asumimos YYYYMMDD
                fecha_dt = datetime.strptime(fecha_numerica, "%Y%m%d").date()
            elif len(fecha_numerica) == 10:
                # Asumimos YYYY-MM-DD
                fecha_dt = datetime.strptime(fecha_predicha, "%Y-%m-%d").date()
            else:
                print(f"[!] Formato de fecha OCR no reconocido: {fecha_predicha}")

            if fecha_dt:
                fecha_desde = datetime.strptime(datos_referencia["fecha_desde"], "%Y-%m-%d").date()
                fecha_hasta = datetime.strptime(datos_referencia["fecha_hasta"], "%Y-%m-%d").date()
                resultado["fecha_valida"] = fecha_desde <= fecha_dt <= fecha_hasta

        except Exception as e:
            print(f"[!] Error validando la fecha: {e}")
            resultado["fecha_valida"] = False

    return resultado
