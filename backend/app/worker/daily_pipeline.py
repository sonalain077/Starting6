"""
PIPELINE QUOTIDIEN - Mise à jour automatique des scores NBA
Exécution : Tous les jours à 8h00 (Eastern Time)

Ce script orchestre toutes les tâches nécessaires pour :
1. Récupérer les stats NBA de la veille
2. Calculer les scores fantasy des joueurs
3. Calculer les scores d'équipe
4. Mettre à jour le leaderboard

Utilisation :
    python backend/app/worker/daily_pipeline.py
    
Ou avec une date spécifique pour tester :
    python backend/app/worker/daily_pipeline.py --date 2024-11-20
"""
import logging
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
import pytz
import argparse

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.worker.tasks.fetch_boxscores import fetch_yesterday_boxscores
from app.worker.tasks.calculate_team_scores import calculate_yesterday_team_scores
from app.worker.tasks.update_leaderboards import update_leaderboards

# Configuration du logging (avec création du dossier)
import os
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'daily_pipeline.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def get_nba_game_date(target_date: date = None) -> date:
    """
    Détermine la date des matchs NBA à traiter
    
    Logique NBA :
    - Les matchs se jouent entre 19h et 2h du matin
    - Si on est avant 12h, on prend les matchs de J-1
    - Si on est après 12h, on prend les matchs de J (qui ne sont pas encore joués)
    
    Args:
        target_date: Date spécifique (pour tests), sinon date automatique
    
    Returns:
        Date des matchs à traiter
    """
    if target_date:
        return target_date
    
    now = datetime.now(pytz.timezone('America/New_York'))
    
    # Si on est avant midi, on prend les matchs d'hier
    # (les matchs de 23h sont encore considérés comme "d'hier")
    if now.hour < 12:
        game_date = (now - timedelta(days=1)).date()
    else:
        # Après midi, on attend le lendemain pour avoir les stats complètes
        game_date = (now - timedelta(days=1)).date()
    
    return game_date


def run_daily_pipeline(target_date: date = None):
    """
    Exécute le pipeline complet de mise à jour quotidienne
    
    Args:
        target_date: Date spécifique pour tester (ex: date(2024, 11, 20))
    """
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "🏀 NBA FANTASY - PIPELINE QUOTIDIEN" + " " * 23 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    
    start_time = datetime.now()
    game_date = get_nba_game_date(target_date)
    
    logger.info(f"\n📅 Date ciblée : {game_date.strftime('%A %d %B %Y')}")
    logger.info(f"⏰ Heure d'exécution : {start_time.strftime('%H:%M:%S')}")
    
    try:
        # ========================================================================
        # ÉTAPE 1 : RÉCUPÉRATION DES BOXSCORES NBA
        # ========================================================================
        logger.info("\n" + "─" * 80)
        logger.info("📊 ÉTAPE 1/3 : Récupération des boxscores NBA")
        logger.info("─" * 80)
        
        fetch_yesterday_boxscores()
        logger.info("✅ Boxscores récupérés avec succès")
        
        # ========================================================================
        # ÉTAPE 2 : CALCUL DES SCORES D'ÉQUIPE
        # ========================================================================
        logger.info("\n" + "─" * 80)
        logger.info("🏀 ÉTAPE 2/3 : Calcul des scores d'équipe")
        logger.info("─" * 80)
        
        calculate_yesterday_team_scores()
        logger.info("✅ Scores d'équipe calculés avec succès")
        
        # ========================================================================
        # ÉTAPE 3 : MISE À JOUR DU LEADERBOARD
        # ========================================================================
        logger.info("\n" + "─" * 80)
        logger.info("🏆 ÉTAPE 3/3 : Mise à jour du leaderboard")
        logger.info("─" * 80)
        
        update_leaderboards()
        logger.info("✅ Leaderboard mis à jour avec succès")
        
        # ========================================================================
        # RÉSUMÉ
        # ========================================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 25 + "✅ PIPELINE TERMINÉ" + " " * 33 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info(f"\n📊 Statistiques d'exécution :")
        logger.info(f"   - Début : {start_time.strftime('%H:%M:%S')}")
        logger.info(f"   - Fin : {end_time.strftime('%H:%M:%S')}")
        logger.info(f"   - Durée : {duration:.1f} secondes")
        logger.info(f"   - Date traitée : {game_date}")
        logger.info("\n🎯 Prochaine exécution : demain à 8h00 Eastern Time")
        
    except Exception as e:
        logger.error("\n" + "╔" + "=" * 78 + "╗")
        logger.error("║" + " " * 25 + "❌ ERREUR PIPELINE" + " " * 34 + "║")
        logger.error("╚" + "=" * 78 + "╝")
        logger.error(f"\n❌ Erreur lors de l'exécution du pipeline : {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pipeline quotidien de mise à jour des scores NBA')
    parser.add_argument(
        '--date',
        type=str,
        help='Date spécifique à traiter (format: YYYY-MM-DD, ex: 2024-11-20)',
        default=None
    )
    
    args = parser.parse_args()
    
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            logger.info(f"🎯 Mode TEST : traitement de la date {target_date}")
        except ValueError:
            logger.error(f"❌ Format de date invalide : {args.date}")
            logger.error("   Format attendu : YYYY-MM-DD (ex: 2024-11-20)")
            sys.exit(1)
    
    run_daily_pipeline(target_date)
