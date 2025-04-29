import pytesseract
from PIL import Image
import io

# Ruta de Tesseract para Windows (ajusta si usas Linux o Mac)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Idiomas OCR a usar (deben estar instalados en Tesseract)
IDIOMAS = "spa+eng+cat+glg+eus"

def extraer_texto_ocr(imagen: Image.Image) -> str:
    """
    Extrae el texto de una imagen usando Tesseract OCR en varios idiomas.

    Args:
        imagen (PIL.Image): Imagen en memoria.

    Returns:
        str: Texto extraído.
    """
    try:
        texto = pytesseract.image_to_string(imagen, lang=IDIOMAS)
        return texto.strip()
    except Exception as e:
        return f"ERROR OCR: {str(e)}"
