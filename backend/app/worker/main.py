"""
Point d'entrée du Worker NBA Fantasy League

Ce script démarre le scheduler qui exécute toutes les tâches automatiques :
- Détection des trades NBA
- Synchronisation des joueurs
- Récupération des boxscores
- Calcul des scores fantasy
- Mise à jour des salaires
- Traitement des waivers
- Mise à jour des leaderboards

Usage:
    python -m app.worker.main
    
Ou via Docker:
    docker-compose up worker
"""
import asyncio
import logging
from app.worker.scheduler import start_scheduler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Démarre le worker et le scheduler
    """
    logger.info("=" * 80)
    logger.info("🚀 NBA FANTASY LEAGUE - WORKER STARTING")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🔧 Initialisation du scheduler...")
    
    try:
        # Démarrer le scheduler avec toutes les tâches
        start_scheduler()
        
        logger.info("✅ Worker démarré avec succès !")
        logger.info("")
        logger.info("📋 Tâches quotidiennes :")
        logger.info("  06h00 - 🔍 Détection trades NBA")
        logger.info("  07h00 - 👥 Synchronisation joueurs")
        logger.info("  08h00 - 📊 Récupération boxscores")
        logger.info("  09h00 - 🧮 Calcul scores équipes")
        logger.info("  13h30 - 🏆 Mise à jour leaderboards")
        logger.info("")
        logger.info("📋 Tâches du lundi :")
        logger.info("  10h00 - 💰 Mise à jour salaires")
        logger.info("  13h00 - 🔄 Traitement waivers")
        logger.info("")
        logger.info("⏰ Fuseau horaire : Europe/Paris")
        logger.info("🏀 Horaires adaptés aux matchs NBA côte Ouest")
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Worker en cours d'exécution... (Ctrl+C pour arrêter)")
        logger.info("=" * 80)
        
        # Garder le worker actif indéfiniment
        asyncio.get_event_loop().run_forever()
        
    except (KeyboardInterrupt, SystemExit):
        logger.info("")
        logger.info("🛑 Arrêt du worker demandé...")
        logger.info("👋 Fermeture propre du scheduler...")
        logger.info("✅ Worker arrêté avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur fatale dans le worker : {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
