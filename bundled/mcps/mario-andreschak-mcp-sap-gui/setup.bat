@echo off

REM Call build.bat first
call build.bat

REM Check if .env exists
IF EXIST .env (
    echo Found existing .env file
) ELSE (
    echo No .env found. Please enter your SAP credentials:
    SET /P SAP_SYSTEM="Enter SAP System: "
    SET /P SAP_CLIENT="Enter SAP Client: "
    SET /P SAP_USER="Enter SAP Username: "
    SET /P SAP_PASSWORD="Enter SAP Password: "
    
    REM Write to .env file
    echo SAP_SYSTEM=%SAP_SYSTEM%> .env
    echo SAP_CLIENT=%SAP_CLIENT%>> .env
    echo SAP_USER=%SAP_USER%>> .env
    echo SAP_PASSWORD=%SAP_PASSWORD%>> .env
    
    echo Created .env file with your settings
)

REM Ask about integration
SET /P INTEGRATION="Do you want to integrate with roo, cline, or no integration? (roo/cline/all/none): "
IF /I "%INTEGRATION%"=="roo" (
    call integrate.bat roo
) ELSE IF /I "%INTEGRATION%"=="cline" (
    call integrate.bat cline
) ELSE IF /I "%INTEGRATION%"=="none" (
    echo Skipping integration...
) ELSE IF /I "%INTEGRATION%"=="all" (
    call integrate.bat cline
    call integrate.bat roo
)

REM Ask about automatic testing
SET /P AUTO_TEST="Do you want to run automatic tests? (y/n) recommended=n: "
IF /I "%AUTO_TEST%"=="y" (
    echo Running automatic tests...
    python -m pytest tests/
)

REM Ask about manual testing
SET /P MANUAL_TEST="Do you want to run manual testing mode? (y/n) recommended=y: "
IF /I "%MANUAL_TEST%"=="y" (
    call run.bat debug
)

echo Setup completed successfully!
