"""
Script de test : Récupérer les boxscores d'une date passée avec des données réelles
"""
import sys
sys.path.insert(0, r'C:\Users\phams\Desktop\ProjetFullstack\backend')

import logging
import time
from datetime import datetime
from sqlalchemy.orm import Session

from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

from app.core.database import SessionLocal
from app.models.player import Player
from app.models.player_game_score import PlayerGameScore
from app.worker.tasks.fetch_boxscores import calculate_fantasy_score

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def fetch_boxscores_test_date(test_date_str="2024-11-04"):
    """
    Récupère les boxscores pour une date de test (4 nov 2024)
    """
    logger.info("=" * 80)
    logger.info("📊 RÉCUPÉRATION DES BOXSCORES NBA - TEST")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    games_processed = 0
    scores_saved = 0
    
    try:
        # Date de test
        test_date = datetime.strptime(test_date_str, "%Y-%m-%d")
        
        logger.info(f"📅 Date de test : {test_date_str}")
        
        # Récupérer la liste des matchs
        logger.info("🏀 Récupération de la liste des matchs...")
        scoreboard = scoreboardv2.ScoreboardV2(game_date=test_date_str)
        games = scoreboard.get_data_frames()[0]
        
        if games.empty:
            logger.info("ℹ️  Aucun match trouvé pour cette date")
            return
        
        logger.info(f"✅ {len(games)} match(s) trouvé(s)")
        logger.info(f"   On va traiter les 3 premiers matchs pour le test\n")
        
        # Traiter les 3 premiers matchs
        for _, game in games.head(3).iterrows():
            game_id = game['GAME_ID']
            logger.info(f"🎯 Match {games_processed + 1} : {game_id}")
            
            try:
                # Rate limiting
                time.sleep(0.5)
                
                # Récupérer les stats détaillées du match
                boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                player_stats = boxscore.get_data_frames()[0]
                
                logger.info(f"   {len(player_stats)} joueurs dans ce match")
                
                # Traiter chaque joueur
                players_processed_in_game = 0
                for _, player_row in player_stats.iterrows():
                    # Retrouver le joueur dans notre BDD
                    player = db.query(Player).filter(
                        Player.external_api_id == player_row['PLAYER_ID']
                    ).first()
                    
                    if not player:
                        logger.debug(f"   Joueur {player_row['PLAYER_NAME']} (ID: {player_row['PLAYER_ID']}) non trouvé en BDD")
                        continue
                    
                    # Supprimer le score s'il existe déjà (pour retester)
                    existing_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == player.id,
                        PlayerGameScore.game_date == test_date.date()
                    ).first()
                    
                    if existing_score:
                        db.delete(existing_score)
                    
                    # Calculer le score fantasy
                    stats = {
                        'PTS': player_row.get('PTS', 0) or 0,
                        'REB': player_row.get('REB', 0) or 0,
                        'AST': player_row.get('AST', 0) or 0,
                        'STL': player_row.get('STL', 0) or 0,
                        'BLK': player_row.get('BLK', 0) or 0,
                        'TO': player_row.get('TO', 0) or 0,
                        'PF': player_row.get('PF', 0) or 0,
                        'FGM': player_row.get('FGM', 0) or 0,
                        'FGA': player_row.get('FGA', 0) or 0,
                        'FG3M': player_row.get('FG3M', 0) or 0,
                        'FTM': player_row.get('FTM', 0) or 0,
                        'FTA': player_row.get('FTA', 0) or 0,
                    }
                    
                    fantasy_score = calculate_fantasy_score(stats)
                    
                    # Enregistrer le score
                    game_score = PlayerGameScore(
                        player_id=player.id,
                        game_date=test_date.date(),
                        fantasy_score=fantasy_score,
                        minutes_played=int(player_row.get('MIN', 0) or 0),
                        points=stats['PTS'],
                        rebounds=stats['REB'],
                        assists=stats['AST'],
                        steals=stats['STL'],
                        blocks=stats['BLK'],
                        turnovers=stats['TO']
                    )
                    db.add(game_score)
                    scores_saved += 1
                    players_processed_in_game += 1
                    
                    if fantasy_score >= 40:
                        logger.info(f"   ⭐ {player.full_name} : {fantasy_score} pts fantasy !")
                
                logger.info(f"   ✅ {players_processed_in_game} joueurs enregistrés dans notre BDD")
                games_processed += 1
                
                # Commit après chaque match
                db.commit()
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour le match {game_id} : {e}")
                continue
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ RÉCUPÉRATION TERMINÉE")
        logger.info(f"   Matchs traités : {games_processed}")
        logger.info(f"   Scores enregistrés : {scores_saved}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des boxscores : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Utiliser une date de la saison 2024 avec des données disponibles
    fetch_boxscores_test_date("2024-11-03")
