# Script d'arret du projet NBA Fantasy "Starting Six"
# Arrete tous les services : Frontend + Backend + PostgreSQL

Write-Host "ARRET DU PROJET NBA FANTASY" -ForegroundColor Red
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""

# ============================================================================
# ETAPE 1 : Arreter le Backend (port 8000)
# ============================================================================

Write-Host "Arret du Backend FastAPI..." -ForegroundColor Yellow

try {
    $backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($backendProcess) {
        foreach ($pid in $backendProcess) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Backend arrete" -ForegroundColor Green
    } else {
        Write-Host "Backend non actif" -ForegroundColor Gray
    }
} catch {
    Write-Host "Backend non actif" -ForegroundColor Gray
}

# ============================================================================
# ETAPE 2 : Arreter le Frontend (port 3000)
# ============================================================================

Write-Host "Arret du Frontend Next.js..." -ForegroundColor Yellow

try {
    $frontendProcess = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($frontendProcess) {
        foreach ($pid in $frontendProcess) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Frontend arrete" -ForegroundColor Green
    } else {
        Write-Host "Frontend non actif" -ForegroundColor Gray
    }
} catch {
    Write-Host "Frontend non actif" -ForegroundColor Gray
}

# ============================================================================
# ETAPE 3 : Arreter PostgreSQL (Docker)
# ============================================================================

Write-Host "Arret de PostgreSQL..." -ForegroundColor Yellow

try {
    $container = docker ps --filter "name=nba_fantasy_db" --format "{{.Names}}" 2>$null
    
    if ($container -eq "nba_fantasy_db") {
        docker stop nba_fantasy_db | Out-Null
        Write-Host "PostgreSQL arrete" -ForegroundColor Green
    } else {
        Write-Host "PostgreSQL non actif" -ForegroundColor Gray
    }
} catch {
    Write-Host "PostgreSQL non actif" -ForegroundColor Gray
}

# ============================================================================
# RESUME
# ============================================================================

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host "TOUS LES SERVICES ONT ETE ARRETES" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""
Write-Host "Pour relancer le projet : .\start_project.ps1" -ForegroundColor Cyan
Write-Host ""
