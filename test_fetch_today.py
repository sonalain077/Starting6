"""
Test manuel : Fetch des matchs d'AUJOURD'HUI (pas hier)
Pour vérifier que l'API live fonctionne
"""
import logging
import sys
sys.path.insert(0, 'c:/Users/phams/Desktop/ProjetFullstack/backend')

from datetime import datetime
from sqlalchemy.orm import Session

from nba_api.live.nba.endpoints import scoreboard, boxscore

from app.core.database import SessionLocal
from app.models.player import Player
from app.models.player_game_score import PlayerGameScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_fantasy_score(stats: dict) -> float:
    """Score fantasy"""
    score = 0.0
    score += stats.get('points', 0) * 1.0
    score += stats.get('reboundsTotal', 0) * 1.2
    score += stats.get('assists', 0) * 1.5
    score += stats.get('steals', 0) * 3.0
    score += stats.get('blocks', 0) * 3.0
    score -= stats.get('turnovers', 0) * 1.5
    score -= stats.get('foulsPersonal', 0) * 0.5
    
    fgm = stats.get('fieldGoalsMade', 0)
    fga = stats.get('fieldGoalsAttempted', 0)
    fg_pct = fgm / fga if fga > 0 else 0
    
    if fga >= 10 and fg_pct >= 0.60:
        score += 3
    
    if stats.get('threePointersMade', 0) >= 3:
        score += 2
    
    if stats.get('reboundsTotal', 0) >= 12:
        score += 2
    
    double_stats = sum([
        stats.get('points', 0) >= 10,
        stats.get('reboundsTotal', 0) >= 10,
        stats.get('assists', 0) >= 10,
    ])
    
    if double_stats == 2:
        score += 5
    elif double_stats == 3:
        score += 12
    
    if stats.get('points', 0) >= 30:
        score += 3
    
    if stats.get('turnovers', 0) >= 5:
        score -= 2
    
    return round(score, 1)


def parse_minutes(minutes_str: str) -> int:
    """Parse PT23M12S → 23"""
    if not minutes_str or minutes_str == "PT0M":
        return 0
    
    try:
        minutes_str = minutes_str.replace('PT', '').replace('S', '')
        if 'M' in minutes_str:
            minutes = int(minutes_str.split('M')[0])
            return minutes
        return 0
    except:
        return 0


logger.info("=" * 80)
logger.info("📊 TEST : FETCH DES MATCHS D'AUJOURD'HUI")
logger.info("=" * 80)

db: Session = SessionLocal()
today = datetime.now()

try:
    # Récupérer le scoreboard live
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    
    games = data.get('scoreboard', {}).get('games', [])
    logger.info(f"✅ {len(games)} match(s) trouvé(s)")
    
    # Ne traiter que les matchs terminés
    final_games = [g for g in games if 'Final' in g.get('gameStatusText', '')]
    logger.info(f"🎯 {len(final_games)} match(s) terminé(s)")
    
    if not final_games:
        logger.info("⚠️  Aucun match terminé pour le moment")
        logger.info("\n📋 Status des matchs:")
        for game in games[:5]:
            home = game.get('homeTeam', {}).get('teamTricode', 'N/A')
            away = game.get('awayTeam', {}).get('teamTricode', 'N/A')
            status = game.get('gameStatusText', 'N/A')
            logger.info(f"   {away} @ {home} : {status}")
    else:
        scores_saved = 0
        
        # Traiter chaque match terminé
        for i, game in enumerate(final_games, 1):
            game_id = game.get('gameId')
            home_team = game.get('homeTeam', {}).get('teamTricode', 'N/A')
            away_team = game.get('awayTeam', {}).get('teamTricode', 'N/A')
            
            logger.info(f"\n🎯 Match {i}/{len(final_games)} : {away_team} @ {home_team} ({game_id})")
            
            try:
                # Récupérer les stats
                box = boxscore.BoxScore(game_id=game_id)
                box_data = box.get_dict()
                
                game_info = box_data.get('game', {})
                home_players = game_info.get('homeTeam', {}).get('players', [])
                away_players = game_info.get('awayTeam', {}).get('players', [])
                all_players = home_players + away_players
                
                logger.info(f"   📊 {len(all_players)} joueurs dans ce match")
                
                # Traiter chaque joueur
                for player_data in all_players:
                    player_id_nba = player_data.get('personId')
                    
                    if not player_id_nba:
                        continue
                    
                    # Retrouver le joueur dans notre BDD
                    player = db.query(Player).filter(
                        Player.external_api_id == player_id_nba
                    ).first()
                    
                    if not player:
                        continue
                    
                    # Vérifier si le score existe déjà
                    existing_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == player.id,
                        PlayerGameScore.game_date == today.date()
                    ).first()
                    
                    if existing_score:
                        logger.info(f"   ℹ️  {player.full_name} : Score déjà existant, skip")
                        continue
                    
                    # Récupérer les statistiques
                    stats = player_data.get('statistics', {})
                    
                    # Vérifier que le joueur a joué
                    minutes_str = stats.get('minutes', 'PT0M')
                    if minutes_str == 'PT0M' or not minutes_str:
                        continue
                    
                    # Calculer le score fantasy
                    fantasy_score = calculate_fantasy_score(stats)
                    
                    # Enregistrer le score
                    game_score = PlayerGameScore(
                        player_id=player.id,
                        game_date=today.date(),
                        fantasy_score=fantasy_score,
                        minutes_played=parse_minutes(minutes_str),
                        points=stats.get('points', 0),
                        rebounds=stats.get('reboundsTotal', 0),
                        assists=stats.get('assists', 0),
                        steals=stats.get('steals', 0),
                        blocks=stats.get('blocks', 0),
                        turnovers=stats.get('turnovers', 0)
                    )
                    db.add(game_score)
                    scores_saved += 1
                    
                    logger.info(f"   ✅ {player.full_name} : {fantasy_score} pts fantasy")
                    
            except Exception as e:
                logger.error(f"   ❌ Erreur : {e}")
                import traceback
                traceback.print_exc()
        
        # Commit
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ TERMINÉ")
        logger.info(f"   Matchs traités : {len(final_games)}")
        logger.info(f"   Scores enregistrés : {scores_saved}")
        logger.info("=" * 80)

except Exception as e:
    logger.error(f"❌ Erreur : {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
