#!/bin/bash
# Script d'initialisation automatique pour le conteneur API
# S'exécute au démarrage pour garantir que la base de données est prête

set -e

echo "🚀 INITIALISATION DU BACKEND"
echo "================================"

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "   PostgreSQL non disponible - attente 1s..."
  sleep 1
done
echo "✅ PostgreSQL est prêt!"

# Vérifier si les tables existent
echo ""
echo "🔍 Vérification de la base de données..."
TABLE_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)

if [ "$TABLE_COUNT" -eq "0" ]; then
    echo "⚠️  Base de données vide - Initialisation..."
    python -c "from app.core.init_db import init_db; init_db()"
    echo "✅ Tables créées!"
else
    echo "✅ Base de données déjà initialisée ($TABLE_COUNT tables)"
fi

# Vérifier si les joueurs existent
echo ""
echo "🏀 Vérification des joueurs NBA..."
PLAYER_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM players;" | xargs)

if [ "$PLAYER_COUNT" -eq "0" ]; then
    echo "⚠️  Aucun joueur trouvé - Import en cours..."
    python -c "from app.worker.tasks.sync_players import sync_nba_players; sync_nba_players()"
    echo "✅ Joueurs importés!"
    
    # Corriger les positions et prix immédiatement
    echo ""
    echo "💰 Correction des positions et prix..."
    if [ -f "/app/quick_fix.py" ]; then
        python /app/quick_fix.py
    else
        echo "⚠️  Script quick_fix.py non trouvé - positions par défaut"
    fi
else
    echo "✅ $PLAYER_COUNT joueurs déjà présents"
    
    # Vérifier si les positions sont correctes (pas tous SG)
    SG_COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM players WHERE player_position = 'SG';" | xargs)
    
    if [ "$SG_COUNT" -eq "$PLAYER_COUNT" ]; then
        echo "⚠️  Tous les joueurs sont SG - Correction nécessaire..."
        if [ -f "/app/quick_fix.py" ]; then
            python /app/quick_fix.py
            echo "✅ Positions et prix corrigés!"
        fi
    else
        echo "✅ Positions correctement distribuées"
    fi
fi

echo ""
echo "================================"
echo "✅ INITIALISATION TERMINÉE"
echo "🚀 Démarrage du serveur API..."
echo ""

# Démarrer l'application FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
