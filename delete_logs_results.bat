@echo off
REM Windows helper: delete Robot/generated folders (plain rmdir — no uv).
REM Usage: delete_logs_results.bat    OR    delete_logs_results.bat clean

setlocal
if "%~1"=="" goto clean
if /i "%~1"=="clean" goto clean
echo Usage: delete_logs_results.bat [clean]
echo Removes: results\, logs\, .robocache\
exit /b 1

:clean
echo Cleaning generated artifacts...
if exist results rmdir /s /q results
if exist logs rmdir /s /q logs
if exist .robocache rmdir /s /q .robocache
echo Done.
