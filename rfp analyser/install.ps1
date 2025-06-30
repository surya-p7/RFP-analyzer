Write-Host "Installing RFP Analyzer..."

# Check Tesseract installation
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "Tesseract found at: $tesseractPath"
} else {
    Write-Host "Tesseract not found at default location."
    Write-Host "Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "Make sure to install it to the default location: C:\Program Files\Tesseract-OCR"
    Write-Host "After installing Tesseract, please run this script again."
    exit
}

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip and install build tools
python -m pip install --upgrade pip
python -m pip install wheel setuptools build

# Install PyTorch first (as it's a dependency for paddleocr)
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install paddlepaddle (required for paddleocr)
python -m pip install paddlepaddle

# Install paddleocr
python -m pip install "paddleocr>=2.7.0"

# Install remaining requirements
python -m pip install -r requirements.txt

# Install the package in development mode
python -m pip install -e .

Write-Host "Installation completed successfully!"
Write-Host "Please make sure Tesseract OCR is installed and added to your PATH"
Write-Host "You can download it from: https://github.com/UB-Mannheim/tesseract/wiki"

Write-Host "Installation complete!"
Write-Host "Please make sure Ollama is installed and run:"
Write-Host "ollama pull granite-embedding:278m"
Write-Host ""
Write-Host "To start the application:"
Write-Host "1. Start the FastAPI server: python main.py"
Write-Host "2. In a new terminal, start Streamlit: streamlit run streamlit_app.py" 