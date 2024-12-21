@echo off


REM Get the directory of the running .bat file
set "SCRIPT_DIR=%~dp0"

REM Get the parent directory of the running .bat file
for %%i in ("%SCRIPT_DIR%..") do set "PARENT_DIR=%%~fi"


REM Run the VBScript to create a shortcut with an icon
cscript //nologo %SCRIPT_DIR%\create_crude_shortcut.vbs

SETLOCAL ENABLEDELAYEDEXPANSION

REM Check for Python installation
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Exiting...
    pause
    exit /b
)

REM Check if virtual environment is activated
set "VENV_ACTIVATED=0"
for /f "delims=" %%i in ('echo %VIRTUAL_ENV%') do (
    if "%%i" NEQ "" set "VENV_ACTIVATED=1"
)

REM List possible activation scripts
set "ACTIVATE_SCRIPTS="
for %%f in (%SCRIPT_DIR%.venv\Scripts\activate.bat %SCRIPT_DIR%.venv\Scripts\activate.ps1 %SCRIPT_DIR%.venv\Scripts\activate_this.py %SCRIPT_DIR%.venv\Scripts\activate %SCRIPT_DIR%.venv\Scripts\deactivate.bat %SCRIPT_DIR%.venv\Scripts\deactivate) do (
    if exist %%f set "ACTIVATE_SCRIPTS=!ACTIVATE_SCRIPTS! %%f"
)

REM If virtual environment is not activated, allow user to choose activation script
IF %VENV_ACTIVATED% EQU 0 (
    echo Virtual environment is not activated. Choose an activation script:
    set /a "i=1"
    for %%f in (!ACTIVATE_SCRIPTS!) do (
        echo !i!: %%f
        set /a "i+=1"
    )
    set /p choice="Enter the number of the activation script to use: "
    set "selected_script="
    for /f "tokens=1,2" %%a in ('echo !ACTIVATE_SCRIPTS!') do (
        if %%a EQU %choice% set "selected_script=%%b"
    )
    if "%selected_script%"=="" (
        echo Invalid choice. Exiting...
        pause
        exit /b
    )
    call %selected_script%
)

REM Check if logs directory exists, if not create it
IF NOT EXIST "%PARENT_DIR%logs" mkdir "%PARENT_DIR%logs"

REM Run the Python application and log output
echo Running application...
python %PARENT_DIR%\main.py > "%PARENT_DIR%\logs\app.log" 2>&1

REM Wait for user input before closing
echo Application closed. View the log at %PARENT_DIR%\logs\app.log
pause
