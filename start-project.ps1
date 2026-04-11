param(
    [switch]$StartFrontend,
    [int]$OllamaStartupTimeoutSeconds = 20
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"

function Test-OllamaRunning {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -Method Get -UseBasicParsing -TimeoutSec 2
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForOllama {
    param([int]$TimeoutSeconds)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-OllamaRunning) {
            return $true
        }

        Start-Sleep -Milliseconds 500
    }

    return $false
}

if (-not (Test-OllamaRunning)) {
    Write-Host "Starting Ollama..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized | Out-Null

    if (-not (Wait-ForOllama -TimeoutSeconds $OllamaStartupTimeoutSeconds)) {
        Write-Error "Ollama did not become ready within $OllamaStartupTimeoutSeconds seconds."
        exit 1
    }
}
else {
    Write-Host "Ollama is already running."
}

$backendPortInUse = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $backendPortInUse) {
    Write-Host "Starting FastAPI backend..."
    Start-Process -FilePath $pythonExe -ArgumentList @("-m", "uvicorn", "main:app", "--reload") -WorkingDirectory $projectRoot | Out-Null
}
else {
    Write-Host "Backend is already listening on port 8000."
}

if ($StartFrontend) {
    $frontendPath = Join-Path $projectRoot "frontend"
    $frontendPortInUse = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if (-not $frontendPortInUse) {
        Write-Host "Starting frontend..."
        Start-Process -FilePath "npx" -ArgumentList @("vite", "--host", "127.0.0.1", "--port", "5173") -WorkingDirectory $frontendPath | Out-Null
    }
    else {
        Write-Host "Frontend is already listening on port 5173."
    }
}

Write-Host "Project startup complete."