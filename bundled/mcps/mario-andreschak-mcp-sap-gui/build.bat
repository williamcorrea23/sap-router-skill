@echo off
REM Build script for MCP SAP GUI

REM Set Python path for testing
@REM set PYTHONPATH=%PYTHONPATH%;%CD%\src

REM Install dependencies
@REM npm install pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
npm install --package-lock-only
npm audit fix

REM Build package
python setup.py build

@REM REM Run tests
@REM pytest tests/ -v


