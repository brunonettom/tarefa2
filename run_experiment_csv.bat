@echo off
REM Configurar console
mode con cols=100 lines=30
color 1F
title Experimento AGL com suporte CSV

echo Iniciando experimento de Aprendizagem de Gramatica Artificial (AGL) com suporte CSV...
python agl_experiment_fixed.py
echo.
echo Experimento concluído. Os resultados foram salvos na pasta 'resultados'.
pause
