import pytesseract
from PIL import Image
import io
import platform

# Detectar sistema operativo y ajustar ruta de Tesseract solo si es Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Idiomas OCR a usar (deben estar instalados)
IDIOMAS = "spa+eng+cat+glg+eus"

def extraer_texto_ocr(imagen: Image.Image) -> str:
    """
    Extrae el texto de una imagen usando Tesseract OCR en varios idiomas.

    Args:
        imagen (PIL.Image): Imagen en memoria.

    Returns:
        str: Texto extraído.
    """
    return pytesseract.image_to_string(imagen, lang=IDIOMAS)
