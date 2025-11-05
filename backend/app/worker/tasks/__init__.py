"""
Worker tasks package
Contains all scheduled background tasks
"""
from .detect_trades import detect_nba_trades
from .sync_players import sync_nba_players
from .fetch_boxscores import fetch_yesterday_boxscores
from .calculate_team_scores import calculate_yesterday_team_scores
from .update_salaries import update_all_player_salaries
from .process_waivers import process_waiver_claims
from .update_leaderboards import update_leaderboards

__all__ = [
    'detect_nba_trades',
    'sync_nba_players',
    'fetch_yesterday_boxscores',
    'calculate_yesterday_team_scores',
    'update_all_player_salaries',
    'process_waiver_claims',
    'update_leaderboards',
]
