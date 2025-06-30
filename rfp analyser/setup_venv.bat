@echo off
echo Creating virtual environment...

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

echo Virtual environment created and activated!
echo Now you can run install.bat to install the dependencies. 