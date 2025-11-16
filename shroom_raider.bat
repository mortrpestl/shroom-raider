@echo off

echo Creating virtual environment...
py -3.11 -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    exit /b 1
)

echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    exit /b 1
)

echo Entering Bonus directory...
cd Bonus
if errorlevel 1 (
    echo ERROR: Failed to enter Bonus folder.
    exit /b 1
)

echo Running Shroom Raider...
python shroom_raider.py
if errorlevel 1 (
    echo ERROR: shroom_raider.py crashed.
    exit /b 1
)