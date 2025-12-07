"""
Script one-shot pour corriger les joueurs existants en base
Il va parcourir les joueurs qui ont team_abbreviation == 'UNK' ou position == 'SG' (si suspect)
et tentera de récupérer team/position via commonplayerinfo.

Usage (depuis la racine du repo):
  # activer le venv puis:
  python backend/fix_players_import.py

Attention: l'endpoint commonplayerinfo est soumis à rate-limiting.
Ce script applique une pause de 0.6s entre requêtes. Pour une base importante, exécutez-le
par batches ou en background (worker).
"""

import logging
import time
from sqlalchemy.orm import Session
from nba_api.stats.endpoints import commonplayerinfo

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

# Mapping complet pour toutes les positions NBA
POSITION_MAP = {
    # Positions courtes
    "G": "SG",
    "F": "SF",
    "C": "C",
    "G-F": "SG",
    "F-C": "PF",
    "F-G": "SF",
    # Positions longues (ce que retourne commonplayerinfo)
    "Guard": "SG",
    "Forward": "SF",
    "Center": "C",
    "Guard-Forward": "SG",
    "Forward-Guard": "SG",
    "Forward-Center": "PF",
    "Center-Forward": "C",
    # Positions spécifiques
    "Point Guard": "PG",
    "Shooting Guard": "SG",
    "Small Forward": "SF",
    "Power Forward": "PF",
}

BATCH_SIZE = 1000  # nombre de joueurs à traiter dans une passe (augmenté)
SLEEP_SECONDS = 0.6


def fix_players(batch_limit: int = None):
    db: Session = SessionLocal()
    try:
        query = db.query(Player).filter(
            (Player.team_abbreviation == "UNK") | (Player.position == "SG")
        )
        if batch_limit:
            players = query.limit(batch_limit).all()
        else:
            players = query.all()

        logger.info(f"Found {len(players)} players to check/update")

        updated = 0
        for i, player in enumerate(players, start=1):
            try:
                time.sleep(SLEEP_SECONDS)
                info = commonplayerinfo.CommonPlayerInfo(player_id=player.external_api_id)
                info_df = info.get_data_frames()[0]
                if info_df.empty:
                    continue

                raw_pos = info_df.get('POSITION').values[0]
                raw_team = info_df.get('TEAM_ABBREVIATION').values[0]

                if raw_pos:
                    mapped = POSITION_MAP.get(raw_pos, raw_pos)
                    player.position = mapped

                if raw_team:
                    player.team = raw_team
                    player.team_abbreviation = raw_team

                updated += 1
                if updated % 20 == 0:
                    logger.info(f"   Updated {updated} players so far...")

            except Exception as e:
                logger.warning(f"Failed for {player.full_name} ({player.external_api_id}): {e}")
                continue

        db.commit()
        logger.info(f"Done. Players updated: {updated}")

    except Exception as e:
        logger.error(f"Error in fix_players: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Pour éviter de bloquer trop longtemps en local, limiter par défaut
    fix_players(batch_limit=BATCH_SIZE)
