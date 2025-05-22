@echo off
echo ===================================
echo ==     RUNNING LOCAL PIPELINE    ==
echo ===================================

echo.
echo --- 1. Running tests with pytest ---
pytest
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Pytest failed. Stopping pipeline.
    exit /b %ERRORLEVEL%
)

echo.
echo --- 2. Checking code style with flake8 ---
flake8
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Flake8 found issues. Stopping pipeline.
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Pipeline completed successfully.
