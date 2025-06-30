# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Function to check if port is in use
function Test-PortInUse {
    param($port)
    $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $port)
    try {
        $listener.Start()
        $listener.Stop()
        return $false
    }
    catch {
        return $true
    }
}

# Function to check if Ollama is running
function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..."

# Check if Ollama is running
Write-Host "Checking Ollama status..."
if (-not (Test-OllamaRunning)) {
    Write-Host "Error: Ollama is not running"
    Write-Host "Please start Ollama by running 'ollama serve' in a separate terminal"
    Write-Host "If you see an error about port 11434 being in use, Ollama is already running"
    exit 1
} else {
    Write-Host "Ollama is running"
}

# Kill any existing processes on port 8000
$existingProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "Stopping existing process on port 8000..."
    Stop-Process -Id $existingProcess.OwningProcess -Force
    Start-Sleep -Seconds 2
}

# Start FastAPI server in the background
Write-Host "Starting FastAPI server..."
$serverProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -PassThru

# Wait for server to start
$maxAttempts = 30
$attempt = 0
$serverStarted = $false

Write-Host "Waiting for FastAPI server to start..."
while ($attempt -lt $maxAttempts) {
    if (Test-PortInUse -port 8000) {
        $serverStarted = $true
        break
    }
    Start-Sleep -Seconds 1
    $attempt++
    Write-Host "Attempt $attempt of $maxAttempts..."
}

if (-not $serverStarted) {
    Write-Host "Failed to start FastAPI server. Please check the server window for errors."
    exit 1
}

Write-Host "FastAPI server started successfully!"

# Start Streamlit app
Write-Host "Starting Streamlit interface..."
streamlit run streamlit_app.py 