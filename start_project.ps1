# Script de demarrage automatique du projet NBA Fantasy "Starting Six"
# Lance automatiquement: PostgreSQL (Docker) + Backend FastAPI + Frontend Next.js

Write-Host "NBA FANTASY - STARTING SIX" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""

# ============================================================================
# ETAPE 1 : Verifier Docker
# ============================================================================

Write-Host "Verification de Docker..." -ForegroundColor Yellow

try {
    $dockerRunning = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Docker n'est pas demarre !" -ForegroundColor Red
        Write-Host "Veuillez lancer Docker Desktop et reessayer." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Docker est actif" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Docker n'est pas installe ou inaccessible" -ForegroundColor Red
    exit 1
}

# ============================================================================
# ETAPE 2 : Demarrer PostgreSQL
# ============================================================================

Write-Host "Demarrage de PostgreSQL..." -ForegroundColor Yellow

$container = docker ps -a --filter "name=nba_fantasy_db" --format "{{.Names}}" 2>$null

if ($container -eq "nba_fantasy_db") {
    $isRunning = docker ps --filter "name=nba_fantasy_db" --format "{{.Names}}" 2>$null
    
    if ($isRunning -eq "nba_fantasy_db") {
        Write-Host "PostgreSQL deja en cours d'execution" -ForegroundColor Green
    } else {
        Write-Host "Demarrage du conteneur existant..." -ForegroundColor Gray
        docker start nba_fantasy_db | Out-Null
        Start-Sleep -Seconds 3
        Write-Host "PostgreSQL demarre" -ForegroundColor Green
    }
} else {
    Write-Host "Creation du conteneur PostgreSQL..." -ForegroundColor Gray
    docker-compose up -d db 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    Write-Host "PostgreSQL cree et demarre" -ForegroundColor Green
}

# Attendre que PostgreSQL soit pret
Write-Host "Attente de la disponibilite de PostgreSQL..." -ForegroundColor Gray
$maxAttempts = 15
$attempt = 0
$pgReady = $false

while ($attempt -lt $maxAttempts -and -not $pgReady) {
    $attempt++
    try {
        $testConnection = docker exec nba_fantasy_db pg_isready -U postgres 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pgReady = $true
        } else {
            Start-Sleep -Seconds 1
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($pgReady) {
    Write-Host "PostgreSQL est pret (port 5432)" -ForegroundColor Green
} else {
    Write-Host "ERREUR: PostgreSQL n'a pas demarre dans le delai imparti" -ForegroundColor Red
    exit 1
}

# ============================================================================
# ETAPE 3 : Demarrer le Backend (FastAPI)
# ============================================================================

Write-Host "Demarrage du Backend FastAPI..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detecte: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installe ou inaccessible" -ForegroundColor Red
    exit 1
}

Write-Host "Lancement du serveur FastAPI sur http://0.0.0.0:8000..." -ForegroundColor Gray

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
)

Write-Host "Attente du demarrage du backend..." -ForegroundColor Gray
Start-Sleep -Seconds 5

$maxAttempts = 20
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($backendReady) {
    Write-Host "Backend FastAPI demarre (http://localhost:8000)" -ForegroundColor Green
    Write-Host "Swagger docs : http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "Backend demarre mais pas encore accessible (normal, peut prendre quelques secondes)" -ForegroundColor Yellow
}

# ============================================================================
# ETAPE 4 : Demarrer le Frontend (Next.js)
# ============================================================================

Write-Host "Demarrage du Frontend Next.js..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js detecte: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Node.js n'est pas installe ou inaccessible" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$PSScriptRoot\frontend\node_modules")) {
    Write-Host "Installation des dependances npm (premiere fois)..." -ForegroundColor Yellow
    Push-Location "$PSScriptRoot\frontend"
    npm install | Out-Null
    Pop-Location
    Write-Host "Dependances installees" -ForegroundColor Green
}

Write-Host "Lancement du serveur Next.js sur http://localhost:3000..." -ForegroundColor Gray

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\frontend'; npm run dev"
)

Write-Host "Attente du demarrage du frontend..." -ForegroundColor Gray
Start-Sleep -Seconds 8

$maxAttempts = 30
$attempt = 0
$frontendReady = $false

while ($attempt -lt $maxAttempts -and -not $frontendReady) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($frontendReady) {
    Write-Host "Frontend Next.js demarre (http://localhost:3000)" -ForegroundColor Green
} else {
    Write-Host "Frontend demarre mais pas encore accessible (compilation en cours...)" -ForegroundColor Yellow
}

# ============================================================================
# RESUME
# ============================================================================

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host "PROJET LANCE AVEC SUCCES !" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""

Write-Host "Services actifs :" -ForegroundColor Cyan
Write-Host ""
Write-Host "   PostgreSQL  : localhost:5432" -ForegroundColor White
Write-Host "   Backend API : http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend    : http://localhost:3000" -ForegroundColor White
Write-Host ""

Write-Host "Documentation API :" -ForegroundColor Cyan
Write-Host "   Swagger UI : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Write-Host "Acces rapides :" -ForegroundColor Cyan
Write-Host "   Accueil      : http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Inscription  : http://localhost:3000/register" -ForegroundColor Cyan
Write-Host "   Connexion    : http://localhost:3000/login" -ForegroundColor Cyan
Write-Host "   Dashboard    : http://localhost:3000/dashboard" -ForegroundColor Cyan
Write-Host ""

Write-Host "IMPORTANT :" -ForegroundColor Yellow
Write-Host "   Deux fenetres PowerShell vont rester ouvertes (Backend + Frontend)" -ForegroundColor Gray
Write-Host "   NE LES FERMEZ PAS pour garder les serveurs actifs" -ForegroundColor Gray
Write-Host "   Pour arreter le projet, fermez ces fenetres ou faites CTRL+C dans chacune" -ForegroundColor Gray
Write-Host ""

Write-Host "Pour arreter tout le projet :" -ForegroundColor Cyan
Write-Host "   Executez : .\stop_project.ps1" -ForegroundColor Yellow
Write-Host ""

Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""
Write-Host "Bonne session de developpement !" -ForegroundColor Green
Write-Host ""
