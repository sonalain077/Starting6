"""
Tâche : Récupération des Boxscores NBA (VERSION 2 - API LIVE)
Exécution : Tous les jours à 08h00

VERSION AMÉLIORÉE utilisant nba_api.live.nba pour accès temps réel
Récupère les statistiques détaillées de tous les matchs de la veille
Calcule les scores fantasy et les enregistre dans PlayerGameScore
"""
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from nba_api.live.nba.endpoints import scoreboard, boxscore
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

from app.core.database import SessionLocal
from app.models.player import Player
from app.models.player_game_score import PlayerGameScore

logger = logging.getLogger(__name__)

def calculate_fantasy_score(stats: dict) -> float:
    """
    Calcule le score fantasy d'un joueur selon le barème officiel
    
    COMPATIBLE avec les 2 formats d'API:
    - API live : 'points', 'reboundsTotal', 'assists', etc.
    - API stats : 'PTS', 'REB', 'AST', etc.
    
    Barème de base :
    - PTS : +1.0 par point
    - REB : +1.2 par rebond
    - AST : +1.5 par passe
    - STL : +3.0 par interception
    - BLK : +3.0 par contre
    - TO : -1.5 par balle perdue
    - PF : -0.5 par faute
    
    Bonus d'efficacité :
    - FG% ≥ 60% (≥10 tentatives) : +3
    - 3PT ≥ 3 réussis : +2
    - FT% = 100% (≥4 tentatives) : +1
    - STL + BLK ≥ 4 : +2
    - REB ≥ 12 : +2
    
    Bonus de performance :
    - Double-Double : +5
    - Triple-Double : +12
    - 30+ points : +3
    - ≥5 TO : -2
    """
    score = 0.0
    
    # Supporter les 2 formats d'API (live et stats)
    pts = stats.get('points', stats.get('PTS', 0))
    reb = stats.get('reboundsTotal', stats.get('REB', 0))
    ast = stats.get('assists', stats.get('AST', 0))
    stl = stats.get('steals', stats.get('STL', 0))
    blk = stats.get('blocks', stats.get('BLK', 0))
    to = stats.get('turnovers', stats.get('TO', 0))
    pf = stats.get('foulsPersonal', stats.get('PF', 0))
    
    # Barème de base
    score += pts * 1.0
    score += reb * 1.2
    score += ast * 1.5
    score += stl * 3.0
    score += blk * 3.0
    score -= to * 1.5
    score -= pf * 0.5
    
    # Bonus d'efficacité
    fgm = stats.get('fieldGoalsMade', stats.get('FGM', 0))
    fga = stats.get('fieldGoalsAttempted', stats.get('FGA', 0))
    fg_pct = fgm / fga if fga > 0 else 0
    
    if fga >= 10 and fg_pct >= 0.60:
        score += 3
    
    fg3m = stats.get('threePointersMade', stats.get('FG3M', 0))
    if fg3m >= 3:
        score += 2
    
    ftm = stats.get('freeThrowsMade', stats.get('FTM', 0))
    fta = stats.get('freeThrowsAttempted', stats.get('FTA', 0))
    if fta >= 4 and ftm == fta:
        score += 1
    
    if (stl + blk) >= 4:
        score += 2
    
    if reb >= 12:
        score += 2
    
    # Bonus de performance
    double_stats = sum([
        pts >= 10,
        reb >= 10,
        ast >= 10,
        stl >= 10,
        blk >= 10,
    ])
    
    if double_stats == 2:
        score += 5
    elif double_stats == 3:
        score += 12
    elif double_stats >= 4:
        score += 25
    
    if pts >= 30:
        score += 3
    
    if to >= 5:
        score -= 2
    
    return round(score, 1)


def parse_minutes(minutes_str: str) -> int:
    """Parse le format ISO 8601 des minutes (ex: "PT23M12S" → 23)"""
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


def fetch_yesterday_boxscores():
    """
    Récupère tous les boxscores des matchs de la veille via API LIVE
    
    NOUVELLE APPROCHE :
    1. Utiliser live.nba.scoreboard pour les matchs récents
    2. Filtrer les matchs terminés (status "Final")  
    3. Pour chaque match, récupérer les stats via live.nba.boxscore
    4. Calculer le score fantasy de chaque joueur
    5. Enregistrer dans PlayerGameScore
    
    FALLBACK :
    Si l'API live ne retourne rien, utiliser l'ancienne méthode stats.endpoints
    """
    logger.info("=" * 80)
    logger.info("📊 RÉCUPÉRATION DES BOXSCORES NBA - VERSION LIVE")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    games_processed = 0
    scores_saved = 0
    yesterday = datetime.now() - timedelta(days=1)
    
    try:
        logger.info(f"📅 Date cible : {yesterday.strftime('%Y-%m-%d')}")
        
        # ÉTAPE 1 : Récupérer le scoreboard live
        logger.info("🏀 Récupération du scoreboard live...")
        board = scoreboard.ScoreBoard()
        data = board.get_dict()
        
        games = data.get('scoreboard', {}).get('games', [])
        logger.info(f"✅ {len(games)} match(s) trouvé(s)")
        
        if not games:
            logger.info("⚠️  Aucun match trouvé, tentative avec stats.endpoints...")
            return fetch_yesterday_boxscores_fallback(db, yesterday)
        
        # ÉTAPE 2 : Filtrer les matchs terminés d'hier
        yesterday_games = []
        for game in games:
            game_status = game.get('gameStatusText', '')
            game_date_str = game.get('gameTimeUTC', '')
            
            # Vérifier si le match est terminé
            if 'Final' not in game_status:
                continue
            
            # Vérifier si c'est un match d'hier (avec une marge de 24h)
            if game_date_str:
                try:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                    game_date_local = game_date.replace(tzinfo=None)
                    
                    time_diff = abs((game_date_local - yesterday).total_seconds())
                    if time_diff < 86400:  # 24 heures
                        yesterday_games.append(game)
                except:
                    if 'Final' in game_status:
                        yesterday_games.append(game)
        
        logger.info(f"🎯 {len(yesterday_games)} match(s) terminé(s) d'hier")
        
        if not yesterday_games:
            logger.info("⚠️  Aucun match d'hier, vérification avec stats.endpoints...")
            return fetch_yesterday_boxscores_fallback(db, yesterday)
        
        # ÉTAPE 3 : Traiter chaque match
        for i, game in enumerate(yesterday_games, 1):
            game_id = game.get('gameId')
            home_team = game.get('homeTeam', {}).get('teamTricode', 'N/A')
            away_team = game.get('awayTeam', {}).get('teamTricode', 'N/A')
            
            logger.info(f"\n🎯 Match {i}/{len(yesterday_games)} : {away_team} @ {home_team} ({game_id})")
            
            try:
                time.sleep(0.5)
                
                box = boxscore.BoxScore(game_id=game_id)
                box_data = box.get_dict()
                
                game_info = box_data.get('game', {})
                home_players = game_info.get('homeTeam', {}).get('players', [])
                away_players = game_info.get('awayTeam', {}).get('players', [])
                all_players = home_players + away_players
                
                logger.info(f"   📊 {len(all_players)} joueurs dans ce match")
                
                for player_data in all_players:
                    player_id_nba = player_data.get('personId')
                    
                    if not player_id_nba:
                        continue
                    
                    player = db.query(Player).filter(
                        Player.external_api_id == player_id_nba
                    ).first()
                    
                    if not player:
                        continue
                    
                    existing_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == player.id,
                        PlayerGameScore.game_date == yesterday.date()
                    ).first()
                    
                    if existing_score:
                        continue
                    
                    stats = player_data.get('statistics', {})
                    
                    minutes_str = stats.get('minutes', 'PT0M')
                    if minutes_str == 'PT0M' or not minutes_str:
                        continue
                    
                    fantasy_score = calculate_fantasy_score(stats)
                    
                    game_score = PlayerGameScore(
                        player_id=player.id,
                        game_date=yesterday.date(),
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
                    
                    if fantasy_score >= 40:
                        logger.info(f"   ⭐ {player.full_name} : {fantasy_score} pts fantasy !")
                
                games_processed += 1
                
                if games_processed % 5 == 0:
                    db.commit()
                    logger.info(f"   💾 {scores_saved} scores sauvegardés jusqu'ici")
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour le match {game_id} : {e}")
                continue
        
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ RÉCUPÉRATION TERMINÉE (API LIVE)")
        logger.info(f"   Matchs traités : {games_processed}")
        logger.info(f"   Scores enregistrés : {scores_saved}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération via API live : {e}")
        logger.info("🔄 Tentative avec stats.endpoints (fallback)...")
        import traceback
        traceback.print_exc()
        
        return fetch_yesterday_boxscores_fallback(db, yesterday)
    finally:
        db.close()


def fetch_yesterday_boxscores_fallback(db: Session, yesterday: datetime):
    """Méthode fallback utilisant stats.endpoints (ancienne méthode)"""
    logger.info("")
    logger.info("🔄 FALLBACK : Utilisation de stats.endpoints")
    logger.info("=" * 80)
    
    games_processed = 0
    scores_saved = 0
    
    try:
        game_date = yesterday.strftime("%Y-%m-%d")
        logger.info(f"📅 Date cible : {game_date}")
        
        scoreboard_v2 = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard_v2.get_data_frames()[0]
        
        if games.empty:
            logger.info("ℹ️  Aucun match trouvé pour cette date")
            return
        
        logger.info(f"✅ {len(games)} match(s) trouvé(s)")
        
        for _, game in games.iterrows():
            game_id = game['GAME_ID']
            logger.info(f"\n🎯 Match {games_processed + 1}/{len(games)} : {game_id}")
            
            try:
                time.sleep(0.5)
                
                boxscore_v2 = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                player_stats = boxscore_v2.get_data_frames()[0]
                
                logger.info(f"   {len(player_stats)} joueurs dans ce match")
                
                for _, player_row in player_stats.iterrows():
                    player = db.query(Player).filter(
                        Player.external_api_id == player_row['PLAYER_ID']
                    ).first()
                    
                    if not player:
                        continue
                    
                    existing_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == player.id,
                        PlayerGameScore.game_date == yesterday.date()
                    ).first()
                    
                    if existing_score:
                        continue
                    
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
                    
                    game_score = PlayerGameScore(
                        player_id=player.id,
                        game_date=yesterday.date(),
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
                    
                    if fantasy_score >= 40:
                        logger.info(f"   ⭐ {player.full_name} : {fantasy_score} pts fantasy !")
                
                games_processed += 1
                
                if games_processed % 5 == 0:
                    db.commit()
                    logger.info(f"   💾 {scores_saved} scores sauvegardés jusqu'ici")
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour le match {game_id} : {e}")
                continue
        
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ RÉCUPÉRATION TERMINÉE (FALLBACK)")
        logger.info(f"   Matchs traités : {games_processed}")
        logger.info(f"   Scores enregistrés : {scores_saved}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du fallback : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_yesterday_boxscores()
