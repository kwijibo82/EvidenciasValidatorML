@echo off
echo Entrenando modelos de evidencia...
python -c "from app.services.trainer import entrenar_modelos; entrenar_modelos()"
pause
