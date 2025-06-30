# RFP Analyzer

An intelligent RFP (Request for Proposal) document analysis system that provides accurate, grounded answers using semantic search and advanced NLP techniques.

## Features

- PDF text extraction with OCR support
- Smart abbreviation resolution
- Semantic search with context-aware retrieval
- Non-hallucinating, grounded answers
- Support for indirect language interpretation
- Comprehensive RFP summary generation
- User-friendly Streamlit interface
- Export summaries as PDF or PowerPoint

## Prerequisites

- Python 3.8 or higher
- Windows 10/11
- CUDA-compatible GPU (recommended for better performance)
- Ollama installed on your system

## Installation

### Windows Installation (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd rfp-analyzer
```

2. Run the installation script:
```bash
install.bat
```

This script will:
- Create a virtual environment
- Install all required dependencies
- Set up PyTorch with CUDA support
- Install the project in development mode

### Manual Installation

If you prefer to install manually:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install build tools:
```bash
pip install wheel setuptools build
```

3. Install PyTorch with CUDA support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

4. Install the project:
```bash
pip install -e .
```

5. Install Ollama and required models:
```bash
ollama pull granite-embedding:278m
```

## Usage

1. Start the FastAPI server:
```bash
python main.py
```

2. In a new terminal, start the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

3. Open your browser and navigate to `http://localhost:8501`

### Web Interface Features

- Upload RFP documents (PDF)
- Ask questions about the RFP
- Generate comprehensive summaries
- Export summaries as PDF or PowerPoint
- Interactive question-answering interface

### API Endpoints

- POST `/analyze`: Submit an RFP document for analysis
- POST `/query`: Ask questions about the RFP
- GET `/summary`: Get a comprehensive summary of the RFP

## Troubleshooting

### Common Issues

1. **Build Errors**
   - Make sure you have the latest version of pip, wheel, and setuptools
   - Try installing build dependencies first: `pip install wheel setuptools build`

2. **CUDA Issues**
   - Verify CUDA installation: `nvidia-smi`
   - Install appropriate PyTorch version for your CUDA version

3. **Ollama Issues**
   - Ensure Ollama is running: `ollama serve`
   - Verify model installation: `ollama list`

## Architecture

- Document Preprocessing: PDF extraction and OCR
- Smart Chunking: Section-wise with fallback to semantic chunks
- Vector Search: Using FAISS/ChromaDB with semantic embeddings
- Context Assembly: Intelligent context combination with abbreviation resolution
- Response Generation: Using IBM Granite 3.2 for accurate, grounded responses
- User Interface: Streamlit for easy interaction
- Export Options: PDF and PowerPoint generation 