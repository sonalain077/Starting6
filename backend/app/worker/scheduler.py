"""
Configuration du Scheduler APScheduler
Gère toutes les tâches planifiées du worker

Horaires (Europe/Paris) :
- 06h00 : Détection des trades NBA
- 07h00 : Synchronisation des joueurs
- 08h00 : Récupération des boxscores
- 09h00 : Calcul des scores des équipes
- 10h00 (Lundi) : Mise à jour des salaires
- 13h00 (Lundi) : Traitement des waivers
- 13h30 : Mise à jour des leaderboards
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Import des tâches
from app.worker.tasks.detect_trades import detect_nba_trades
from app.worker.tasks.sync_players import sync_nba_players
from app.worker.tasks.fetch_boxscores import fetch_yesterday_boxscores
from app.worker.tasks.calculate_team_scores import calculate_yesterday_team_scores
from app.worker.tasks.update_salaries import update_all_player_salaries
from app.worker.tasks.process_waivers import process_waiver_claims
from app.worker.tasks.update_leaderboards import update_leaderboards

logger = logging.getLogger(__name__)

# Initialiser le scheduler avec le fuseau horaire de Paris
scheduler = AsyncIOScheduler(timezone="Europe/Paris")

def start_scheduler():
    """
    Configure et démarre le scheduler avec toutes les tâches planifiées
    
    Les horaires sont adaptés pour prendre en compte les matchs NBA
    de la côte Ouest qui peuvent se terminer vers 5h du matin (heure Paris)
    """
    
    # ========================================
    # TÂCHES QUOTIDIENNES
    # ========================================
    
    # 06h00 : Détection des trades NBA
    scheduler.add_job(
        detect_nba_trades,
        CronTrigger(hour=6, minute=0),
        id="detect_trades",
        name="🔍 Détection trades NBA",
        replace_existing=True,
        misfire_grace_time=3600  # 1h de tolérance si le worker redémarre
    )
    logger.info("📅 Tâche planifiée : 🔍 Détection trades NBA (06h00)")
    
    # 07h00 : Synchronisation de la liste des joueurs NBA
    scheduler.add_job(
        sync_nba_players,
        CronTrigger(hour=7, minute=0),
        id="sync_players",
        name="👥 Synchronisation joueurs NBA",
        replace_existing=True,
        misfire_grace_time=3600
    )
    logger.info("📅 Tâche planifiée : 👥 Synchronisation joueurs (07h00)")
    
    # 08h00 : Récupération des boxscores d'hier
    scheduler.add_job(
        fetch_yesterday_boxscores,
        CronTrigger(hour=8, minute=0),
        id="fetch_boxscores",
        name="📊 Récupération boxscores",
        replace_existing=True,
        misfire_grace_time=3600
    )
    logger.info("📅 Tâche planifiée : 📊 Récupération boxscores (08h00)")
    
    # 09h00 : Calcul des scores des équipes fantasy
    scheduler.add_job(
        calculate_yesterday_team_scores,
        CronTrigger(hour=9, minute=0),
        id="calculate_team_scores",
        name="🧮 Calcul scores équipes",
        replace_existing=True,
        misfire_grace_time=3600
    )
    logger.info("📅 Tâche planifiée : 🧮 Calcul scores équipes (09h00)")
    
    # 13h30 : Mise à jour des leaderboards
    scheduler.add_job(
        update_leaderboards,
        CronTrigger(hour=13, minute=30),
        id="update_leaderboards",
        name="🏆 Mise à jour leaderboards",
        replace_existing=True,
        misfire_grace_time=3600
    )
    logger.info("📅 Tâche planifiée : 🏆 Mise à jour leaderboards (13h30)")
    
    # ========================================
    # TÂCHES DU LUNDI (Jour de Transferts)
    # ========================================
    
    # 10h00 (Lundi) : Mise à jour des salaires fantasy
    scheduler.add_job(
        update_all_player_salaries,
        CronTrigger(day_of_week='mon', hour=10, minute=0),
        id="update_salaries",
        name="💰 Mise à jour salaires (Lundi)",
        replace_existing=True,
        misfire_grace_time=7200  # 2h de tolérance pour le lundi
    )
    logger.info("📅 Tâche planifiée : 💰 Mise à jour salaires (Lundi 10h00)")
    
    # 13h00 (Lundi) : Traitement des waivers (Private Leagues)
    scheduler.add_job(
        process_waiver_claims,
        CronTrigger(day_of_week='mon', hour=13, minute=0),
        id="process_waivers",
        name="🔄 Traitement waivers (Lundi)",
        replace_existing=True,
        misfire_grace_time=7200
    )
    logger.info("📅 Tâche planifiée : 🔄 Traitement waivers (Lundi 13h00)")
    
    # Démarrer le scheduler
    scheduler.start()
    logger.info("")
    logger.info("✅ Scheduler démarré avec 7 tâches planifiées")
    logger.info("⏰ Timezone : Europe/Paris")
    logger.info("🏀 Adapté aux matchs NBA côte Ouest (fin ~5h)")
    
    return scheduler
