#!/bin/bash

echo "=========================================="
echo "Tests automatisés - NBA Fantasy League"
echo "=========================================="
echo ""

# Installer les dépendances de test
pip install pytest pytest-asyncio httpx

# Lancer les tests avec pytest
pytest tests/ -v --tb=short --color=yes

echo ""
echo "=========================================="
echo "Tests terminés"
echo "=========================================="
