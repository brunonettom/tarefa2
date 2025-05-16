@echo off
REM Configurar para tela cheia
mode con cols=9999 lines=9999
powershell -command "&{$Host.UI.RawUI.WindowSize = $Host.UI.RawUI.MaxWindowSize; $Host.UI.RawUI.BufferSize = $Host.UI.RawUI.MaxWindowSize}"
powershell -command "&{$pshost = Get-Host; $pswindow = $pshost.UI.RawUI; $pswindow.FullScreen = $true}"

echo Iniciando experimento de Aprendizagem de Gramatica Artificial (AGL)...
python agl_experiment.py
