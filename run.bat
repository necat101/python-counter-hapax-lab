@echo off
REM python-counter-hapax-lab runner – Windows
setlocal
cd /d "%~dp0"

REM Find a python interpreter
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 goto :found
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY=py
    goto :found
)
echo error: python not found in PATH
exit /b 1

:found
if not defined PY set PY=python

echo === python-counter-hapax-lab ===
%PY% --version
echo.

echo --- run_lab.py ---
%PY% run_lab.py
set RUNNER_EXIT=%ERRORLEVEL%

echo.
echo --- unittest ---
%PY% -m unittest tests.test_hapax -v
set UNITTEST_EXIT=%ERRORLEVEL%

echo.
if %RUNNER_EXIT% EQU 0 if %UNITTEST_EXIT% EQU 0 (
    echo all checks passed
    exit /b 0
) else (
    echo FAILED ^(run_lab exit=%RUNNER_EXIT%, unittest exit=%UNITTEST_EXIT%^)
    exit /b 1
)
