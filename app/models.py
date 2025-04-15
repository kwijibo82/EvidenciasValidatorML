from pydantic import BaseModel
from datetime import date

class ValidationResult(BaseModel):
    cliente_detectado: str
    autor_detectado: str
    fecha_detectada: str
    cliente_valido: bool
    autor_valido: bool
    fecha_valida: bool