@echo off
echo Installing RFP Analyzer...

:: Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate

:: Upgrade pip and install build tools
python -m pip install --upgrade pip
pip install wheel setuptools build

:: Install paddlepaddle-cpu with increased timeout
pip install --default-timeout=100 paddlepaddle-cpu

:: Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

:: Install ollama package
pip install ollama

:: Install the project
pip install -e .

:: Install Ollama (if not already installed)
echo Please make sure Ollama is installed and run:
echo ollama pull granite-embedding:278m

echo Installation complete!
echo To start the application:
echo 1. Start the FastAPI server: python main.py
echo 2. In a new terminal, start Streamlit: streamlit run streamlit_app.py 