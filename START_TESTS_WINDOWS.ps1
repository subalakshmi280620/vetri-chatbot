$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $ProjectRoot "backend"
$Frontend = Join-Path $ProjectRoot "frontend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$Requirements = Join-Path $Backend "requirements.txt"
$Marker = Join-Path $Backend ".venv\requirements.sha256"

Write-Host "`n=== Vetri AI Coach: local checks ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python is not available. Install Python once, then reopen PowerShell." }
if (-not (Test-Path (Join-Path $Backend "manage.py"))) { throw "backend\manage.py not found. Run this script from the extracted project root." }
if (-not (Test-Path $Requirements)) { throw "backend\requirements.txt not found." }

if (-not (Test-Path $VenvPython)) {
    Write-Host "`nCreating backend virtual environment (this does NOT reinstall Python)..." -ForegroundColor Yellow
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv (Join-Path $Backend ".venv") } else { & python -m venv (Join-Path $Backend ".venv") }
    if ($LASTEXITCODE -ne 0) { throw "Could not create backend .venv." }
}
$ReqHash = (Get-FileHash $Requirements -Algorithm SHA256).Hash
$OldHash = if (Test-Path $Marker) { (Get-Content $Marker -Raw).Trim() } else { "" }
if ($ReqHash -ne $OldHash) {
    Write-Host "`nInstalling/updating backend packages from requirements.txt..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
    & $VenvPython -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }
    Set-Content -Path $Marker -Value $ReqHash -Encoding ascii
} else { Write-Host "Backend dependencies unchanged; skipping reinstall." -ForegroundColor Green }

Push-Location $Backend
try {
    Write-Host "`n=== Django system check ===" -ForegroundColor Cyan
    & $VenvPython manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Django check failed." }
    Write-Host "`n=== Django tests ===" -ForegroundColor Cyan
    & $VenvPython manage.py test chatbot --verbosity 2 2>&1 | Tee-Object -FilePath (Join-Path $ProjectRoot "test-output.txt")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nTests failed. Failure summary:" -ForegroundColor Red
        Select-String -Path (Join-Path $ProjectRoot "test-output.txt") -Pattern '^FAIL:|^ERROR:|AssertionError:|^FAILED|^Ran ' -Context 0,2
        throw "Django tests failed. See test-output.txt. Do not deploy yet."
    }
} finally { Pop-Location }

if (Test-Path $Frontend) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Write-Host "`nSkipping frontend checks: Node.js/npm is not installed." -ForegroundColor Yellow }
    else {
        Push-Location $Frontend
        try {
            if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
                Write-Host "`nInstalling frontend packages (first run only in this folder)..." -ForegroundColor Yellow
                & npm ci
                if ($LASTEXITCODE -ne 0) { throw "npm ci failed." }
            }
            Write-Host "`n=== Frontend lint ===" -ForegroundColor Cyan
            & npm run lint
            if ($LASTEXITCODE -ne 0) { throw "Frontend lint failed." }
            Write-Host "`n=== Frontend build ===" -ForegroundColor Cyan
            & npm run build
            if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
        } finally { Pop-Location }
    }
}
Write-Host "`nAll checks completed successfully." -ForegroundColor Green
