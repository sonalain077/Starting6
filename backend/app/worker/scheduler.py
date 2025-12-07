"""
Configuration du Scheduler APScheduler
Gère toutes les tâches planifiées du worker

Horaires (America/New_York - Eastern Time) :
- 08h00 : Pipeline quotidien complet (boxscores + scores équipes + leaderboard)
- 10h00 (Lundi) : Mise à jour des salaires hebdomadaire

Version MVP Solo League : Simplifié sans trades ni waivers
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Import du pipeline quotidien
from app.worker.daily_pipeline import run_daily_pipeline
from app.worker.tasks.update_salaries import update_all_player_salaries

logger = logging.getLogger(__name__)

# Initialiser le scheduler avec le fuseau horaire Eastern (siège NBA)
scheduler = BackgroundScheduler(timezone="America/New_York")


def start_scheduler():
    """
    Configure et démarre le scheduler avec toutes les tâches planifiées
    
    MODE MVP SOLO LEAGUE :
    - Pipeline quotidien à 8h ET (après les matchs de la nuit)
    - Mise à jour salaires le lundi à 10h ET
    """
    
    logger.info("=" * 80)
    logger.info("⏰ DÉMARRAGE DU SCHEDULER - NBA FANTASY MVP")
    logger.info("=" * 80)
    
    # ========================================
    # TÂCHE QUOTIDIENNE : PIPELINE COMPLET
    # ========================================
    
    # 08h00 ET : Pipeline quotidien (boxscores + scores + leaderboard)
    scheduler.add_job(
        run_daily_pipeline,
        CronTrigger(hour=8, minute=0),
        id="daily_pipeline",
        name="🏀 Pipeline quotidien NBA",
        replace_existing=True,
        misfire_grace_time=3600  # 1h de tolérance si le worker redémarre
    )
    logger.info("📅 Tâche planifiée : 🏀 Pipeline quotidien (08h00 ET)")
    logger.info("   ├─ Récupération boxscores NBA")
    logger.info("   ├─ Calcul scores fantasy joueurs")
    logger.info("   ├─ Calcul scores équipes")
    logger.info("   └─ Mise à jour leaderboard")
    
    # ========================================
    # TÂCHE HEBDOMADAIRE (LUNDI)
    # ========================================
    
    # 10h00 (Lundi) : Mise à jour hebdomadaire des salaires
    scheduler.add_job(
        update_all_player_salaries,
        CronTrigger(day_of_week='mon', hour=10, minute=0),
        id="update_salaries",
        name="💰 Mise à jour salaires",
        replace_existing=True,
        misfire_grace_time=7200  # 2h de tolérance
    )
    logger.info("📅 Tâche planifiée : 💰 Mise à jour salaires (Lundi 10h00 ET)")
    
    # ========================================
    # DÉMARRAGE
    # ========================================
    
    scheduler.start()
    
    logger.info("=" * 80)
    logger.info("✅ SCHEDULER DÉMARRÉ")
    logger.info("=" * 80)
    logger.info("🔄 Le worker est maintenant actif et attend les tâches planifiées")
    logger.info("📋 Liste des jobs programmés :")
    for job in scheduler.get_jobs():
        logger.info(f"   - {job.name} : {job.next_run_time}")
    logger.info("=" * 80)


def stop_scheduler():
    """Arrête proprement le scheduler"""
    logger.info("🛑 Arrêt du scheduler...")
    scheduler.shutdown(wait=True)
    logger.info("✅ Scheduler arrêté")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        start_scheduler()
        
        # Garder le script actif
        import time
        logger.info("\n⏰ Worker en attente des tâches planifiées...")
        logger.info("   Appuyez sur Ctrl+C pour arrêter\n")
        
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n\n🛑 Interruption détectée")
        stop_scheduler()
