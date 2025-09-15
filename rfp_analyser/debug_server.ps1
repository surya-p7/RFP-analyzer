# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing/upgrading dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run FastAPI server with detailed error output
Write-Host "Starting FastAPI server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug 