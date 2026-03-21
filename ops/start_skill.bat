@echo off
REM ops\start_skill.bat — Sigrid Skill Autostart (Windows)
REM
REM Usage:
REM   ops\start_skill.bat                   (openclaw mode, default)
REM   ops\start_skill.bat --mode terminal   (interactive REPL)
REM   ops\start_skill.bat --skip-calibrate  (skip pre-flight checks)
REM
REM Prerequisites:
REM   - Python 3.10+ with all dependencies installed
REM   - .env file at project root (copy from .env.example)
REM   - LiteLLM proxy running (optional for cloud tiers)
REM   - Ollama running (optional for subconscious tier)

SETLOCAL ENABLEEXTENSIONS

REM Resolve project root (one level up from ops\)
SET "SCRIPT_DIR=%~dp0"
SET "PROJECT_ROOT=%SCRIPT_DIR%.."
CD /D "%PROJECT_ROOT%"

ECHO.
ECHO ======================================================================
ECHO   Sigrid Skill -- Autostart (Windows)
ECHO   %DATE% %TIME%
ECHO ======================================================================
ECHO.

REM Load .env if present
IF EXIST ".env" (
    FOR /F "usebackq tokens=1,* delims==" %%A IN (".env") DO (
        IF NOT "%%A"=="" IF NOT "%%A:~0,1%"=="#" (
            SET "%%A=%%B"
        )
    )
    ECHO   [.env loaded]
)

REM Parse --skip-calibrate flag
SET "SKIP_CALIBRATE=0"
SET "EXTRA_ARGS="
FOR %%A IN (%*) DO (
    IF "%%A"=="--skip-calibrate" (
        SET "SKIP_CALIBRATE=1"
    ) ELSE (
        SET "EXTRA_ARGS=%EXTRA_ARGS% %%A"
    )
)

REM Step 1 -- Pre-flight calibration
IF "%SKIP_CALIBRATE%"=="0" (
    ECHO.
    ECHO   Running launch calibration...
    ECHO.
    python ops\launch_calibration.py --config .env
    IF ERRORLEVEL 1 (
        ECHO.
        ECHO   Launch calibration failed. Fix errors above or use --skip-calibrate.
        EXIT /B 1
    )
)

REM Step 2 -- Activate venv if present
IF EXIST "venv\Scripts\activate.bat" (
    ECHO   Activating venv...
    CALL "venv\Scripts\activate.bat"
) ELSE IF EXIST ".venv\Scripts\activate.bat" (
    ECHO   Activating .venv...
    CALL ".venv\Scripts\activate.bat"
)

REM Step 3 -- Launch skill
ECHO.
ECHO   Starting Sigrid skill...
ECHO.

SET "PYTHONPATH=%PROJECT_ROOT%\viking_girlfriend_skill;%PYTHONPATH%"
python "viking_girlfriend_skill\scripts\main.py" %EXTRA_ARGS%

ENDLOCAL
