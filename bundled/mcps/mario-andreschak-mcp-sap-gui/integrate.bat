@echo off
IF "%1"=="" (
    echo Usage: integrate.bat [cline^|roo]
    echo   cline: Update Cline settings
    echo   roo: Update Roo settings
    exit /b 1
)

IF /I "%1"=="cline" (
    python integrate.py cline
) ELSE IF /I "%1"=="roo" (
    python integrate.py roo
) ELSE (
    echo Invalid parameter. Use 'cline' or 'roo'
    exit /b 1
)
