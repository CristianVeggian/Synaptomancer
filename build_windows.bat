@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "PYTHON=%PROJECT_ROOT%.venv\Scripts\python.exe"
set "OUTPUT_DIR=%PROJECT_ROOT%release\Synaptomancer"

if not exist "%PYTHON%" (
  echo Ambiente virtual nao encontrado: %PYTHON%
  echo Crie o ambiente e instale as dependencias antes de gerar o pacote.
  exit /b 1
)

"%PYTHON%" -m PyInstaller --noconfirm --clean --onedir --windowed --name Synaptomancer ^
  --distpath "%PROJECT_ROOT%release" ^
  --workpath "%PROJECT_ROOT%build\pyinstaller" ^
  --specpath "%PROJECT_ROOT%build\pyinstaller" ^
  --runtime-hook "%PROJECT_ROOT%build_hooks\qt_dll_path.py" ^
  --collect-all mne ^
  "%PROJECT_ROOT%main.py"

if errorlevel 1 exit /b %errorlevel%

xcopy "%PROJECT_ROOT%data" "%OUTPUT_DIR%\data\" /E /I /Y >nul
xcopy "%PROJECT_ROOT%translations" "%OUTPUT_DIR%\translations\" /E /I /Y >nul
xcopy "%PROJECT_ROOT%functions\plugins" "%OUTPUT_DIR%\functions\plugins\" /E /I /Y >nul

echo.
echo Pacote criado em: %OUTPUT_DIR%
echo Distribua a pasta Synaptomancer inteira; nao mova somente o .exe.
