Write-Host "Creating virtual environment..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

Write-Host "Virtual environment created and activated!"
Write-Host "Now you can run install.ps1 to install the dependencies." 