@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "DEPLOY_DIR=%~dp0"
if "%DEPLOY_DIR:~-1%"=="\" set "DEPLOY_DIR=%DEPLOY_DIR:~0,-1%"
set "SOURCE_DIR="
set "VENV_DIR=%DEPLOY_DIR%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

for /d %%D in ("%DEPLOY_DIR%\..\*") do (
  if exist "%%~fD\pyproject.toml" (
    set "SOURCE_DIR=%%~fD"
  )
)

if not defined SOURCE_DIR (
  echo 找不到源码目录。要求部署目录的同级目录中存在包含 pyproject.toml 的项目目录。
  exit /b 1
)

pushd "%DEPLOY_DIR%"

if not exist ".env" if exist ".env.example" copy /Y ".env.example" ".env" >nul

set "NEED_INSTALL=0"
if not exist "%PYTHON_EXE%" set "NEED_INSTALL=1"

set "SHOW_HELP=0"
set "RUN_ANALYZE=0"
set "CHECKPOINT=0"
set "CLEAR_CHECKPOINTS=0"

:parse_args
if "%~1"=="" goto after_parse
if /I "%~1"=="--install" set "NEED_INSTALL=1"
if /I "%~1"=="--help" set "SHOW_HELP=1"
if /I "%~1"=="analyze" set "RUN_ANALYZE=1"
if /I "%~1"=="--checkpoint" set "CHECKPOINT=1"
if /I "%~1"=="--clear-checkpoints" set "CLEAR_CHECKPOINTS=1"
shift
goto parse_args

:after_parse
if "%NEED_INSTALL%"=="1" (
  python -m venv "%VENV_DIR%"
  if errorlevel 1 goto fail
  "%PYTHON_EXE%" -m pip install --upgrade pip
  if errorlevel 1 goto fail
  "%PYTHON_EXE%" -m pip install "%SOURCE_DIR%"
  if errorlevel 1 goto fail
)

set "CA_BUNDLE="
for /f "usebackq delims=" %%I in (`"%PYTHON_EXE%" "%DEPLOY_DIR%\prepare_runtime.py"`) do set "CA_BUNDLE=%%I"
if defined CA_BUNDLE (
  set "SSL_CERT_FILE=%CA_BUNDLE%"
  set "REQUESTS_CA_BUNDLE=%CA_BUNDLE%"
  set "CURL_CA_BUNDLE=%CA_BUNDLE%"
)

set PYTHONUTF8=1

if "%SHOW_HELP%"=="1" (
  "%PYTHON_EXE%" -m cli.main --help
  set "EXITCODE=%ERRORLEVEL%"
  goto done
)

if "%RUN_ANALYZE%"=="1" (
  set "ARGS=-m cli.main analyze"
) else (
  set "ARGS=-m cli.main"
)

if "%CHECKPOINT%"=="1" set "ARGS=%ARGS% --checkpoint"
if "%CLEAR_CHECKPOINTS%"=="1" set "ARGS=%ARGS% --clear-checkpoints"

"%PYTHON_EXE%" %ARGS%
set "EXITCODE=%ERRORLEVEL%"
goto done

:fail
set "EXITCODE=%ERRORLEVEL%"

:done
popd
exit /b %EXITCODE%