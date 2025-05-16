@echo off
echo Instalando dependencias para o experimento AGL...
pip install -r requirements.txt
echo.
echo Preparacao concluida! Pressione qualquer tecla para iniciar o experimento...
pause > nul
python agl_experiment.py
