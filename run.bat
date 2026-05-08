@echo off
REM Automotive Test Framework - Windows Batch Helper
REM Usage: run.bat [command]

setlocal enabledelayedexpansion

if "%1"=="" (
    call :show_menu
) else (
    call :!1!
)
goto :eof

:show_menu
cls
echo.
echo ============================================================
echo   AUTOMOTIVE TEST FRAMEWORK - COMMAND MENU
echo ============================================================
echo.
echo Setup and Installation:
echo   run setup              - Run setup verification
echo   run install            - Install dependencies
echo.
echo Testing:
echo   run test               - Run all tests
echo   run test-smoke         - Run smoke tests only
echo   run test-integration   - Run integration tests only
echo   run test-speed         - Run specific speed test
echo   run test-report        - Run tests with HTML report
echo.
echo Examples and Documentation:
echo   run examples           - Show usage examples
echo   run quickstart         - Interactive quick start menu
echo   run docs               - Show documentation links
echo.
echo Utilities:
echo   run clean              - Clean generated files
echo   run help               - Show this menu
echo.
echo ============================================================
echo.
set /p choice="Enter command: "
if defined choice (
    call :%choice%
) else (
    goto :show_menu
)
goto :eof

:setup
echo.
echo Running setup verification...
python setup_project.py
pause
goto :eof

:install
echo.
echo Installing dependencies...
uv pip install robotframework cantools python-can
pause
goto :eof

:test
echo.
echo Running all tests...
robot tests/
pause
goto :eof

:test-smoke
echo.
echo Running smoke tests...
robot tests/smoke_tests.robot
pause
goto :eof

:test-integration
echo.
echo Running integration tests...
robot tests/integration_tests.robot
pause
goto :eof

:test-speed
echo.
echo Running high speed test...
robot -t "Verify High Speed Behavior" tests/smoke_tests.robot
pause
goto :eof

:test-report
echo.
echo Running tests with HTML report...
robot --outputdir ./results tests/
echo.
echo Test report generated in: results/report.html
echo Opening report...
start results\report.html
pause
goto :eof

:examples
echo.
echo Showing usage examples...
python examples.py
pause
goto :eof

:quickstart
echo.
echo Starting interactive quick start...
python quickstart.py
pause
goto :eof

:docs
echo.
echo ============================================================
echo   DOCUMENTATION LINKS
echo ============================================================
echo.
echo Main documentation: README.md
echo Quick start guide: QUICKSTART.md
echo Technical details: TECHNICAL_DOCUMENTATION.md
echo Usage examples: python examples.py
echo.
echo To read documentation in VS Code:
echo   - Open the files in VS Code
echo   - Or use Ctrl+K Ctrl+O to open file
echo.
pause
goto :eof

:clean
echo.
echo Cleaning up test artifacts...
if exist results (
    rmdir /s /q results
    echo Removed: results/
)
if exist logs (
    rmdir /s /q logs
    echo Removed: logs/
)
if exist .robocache (
    rmdir /s /q .robocache
    echo Removed: .robocache/
)
echo.
echo Cleanup complete!
pause
goto :eof

:help
call :show_menu
goto :eof

echo.
echo Invalid command: %1
echo Run without arguments to see menu
pause
