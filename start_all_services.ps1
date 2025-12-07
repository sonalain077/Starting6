#!/usr/bin/env pwsh

Write-Host ""
Write-Host "🚀 STARTING SIX - NBA Fantasy League MVP" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""

# Vérifier Docker
Write-Host "🔍 Vérification de Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Out-String
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker n'est pas démarré !" -ForegroundColor Red
    Write-Host "   Démarrez Docker Desktop puis relancez ce script." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker est actif" -ForegroundColor Green

# Arrêter les anciens conteneurs
Write-Host ""
Write-Host "🛑 Arrêt des anciens services..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null

# Construire les images
Write-Host ""
Write-Host "🔨 Construction des images Docker..." -ForegroundColor Cyan
Write-Host "   (Cela peut prendre 2-3 minutes la première fois)" -ForegroundColor DarkGray
docker-compose build --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la construction des images" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Images construites avec succès" -ForegroundColor Green

# Démarrer tous les services
Write-Host ""
Write-Host "▶️  Démarrage de tous les services..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du démarrage des services" -ForegroundColor Red
    exit 1
}

# Attendre que les services démarrent
Write-Host ""
Write-Host "⏳ Attente du démarrage complet..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    Write-Progress -Activity "Initialisation des services" -Status "Temps écoulé : $i secondes" -PercentComplete ($i / 30 * 100)
    Start-Sleep -Seconds 1
}
Write-Progress -Activity "Initialisation des services" -Completed

# Vérifier le statut des services
Write-Host ""
Write-Host "📊 Statut des services:" -ForegroundColor Cyan
Write-Host ""
docker-compose ps

# Afficher les logs du worker (dernières lignes)
Write-Host ""
Write-Host "📋 Logs du Worker (dernières 15 lignes):" -ForegroundColor Cyan
Write-Host "-" * 70 -ForegroundColor DarkGray
docker-compose logs --tail=15 worker
Write-Host "-" * 70 -ForegroundColor DarkGray

# Résumé final
Write-Host ""
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host "✅ TOUS LES SERVICES SONT DÉMARRÉS !" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""

Write-Host "📌 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host "   🔌 Backend API:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "   📚 API Docs:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "   🗄️  Database:    " -NoNewline -ForegroundColor White
Write-Host "localhost:5432" -ForegroundColor Blue
Write-Host ""

Write-Host "🤖 Worker actif:" -ForegroundColor Yellow
Write-Host "   • Calcul automatique des scores quotidiens à 8h00 ET" -ForegroundColor White
Write-Host "   • Mise à jour des salaires tous les lundis à 10h00 ET" -ForegroundColor White
Write-Host ""

Write-Host "Commandes utiles:" -ForegroundColor Cyan
Write-Host "   Logs en temps reel:       docker-compose logs -f" -ForegroundColor White
Write-Host "   Logs du worker:           docker-compose logs -f worker" -ForegroundColor White
Write-Host "   Logs du backend:          docker-compose logs -f api" -ForegroundColor White
Write-Host "   Redemarrer un service:    docker-compose restart worker" -ForegroundColor White
Write-Host ""

Write-Host "Arreter tous les services:" -ForegroundColor Red
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""

Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host "🎯 Projet prêt pour la démonstration !" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""
