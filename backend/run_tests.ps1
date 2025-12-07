Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Tests automatisés - NBA Fantasy League" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Installer les dépendances de test
pip install pytest pytest-asyncio httpx

# Lancer les tests avec pytest
pytest tests/ -v --tb=short --color=yes

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Tests terminés" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
