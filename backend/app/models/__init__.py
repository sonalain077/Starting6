"""
Modèles SQLAlchemy - Tous les modèles de la base de données

Ce fichier centralise l'import de tous les modèles.
Cela permet à SQLAlchemy de créer toutes les tables en une seule fois.
"""
from app.models.utilisateur import Utilisateur
from app.models.league import League, LeagueType
from app.models.player import Player, Position
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer, RosterSlot
from app.models.player_game_score import PlayerGameScore
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.transfer import Transfer, TransferType, TransferStatus

__all__ = [
    "Utilisateur",
    "League",
    "LeagueType",
    "Player",
    "Position",
    "FantasyTeam",
    "FantasyTeamPlayer",
    "RosterSlot",
    "PlayerGameScore",
    "FantasyTeamScore",
    "Transfer",
    "TransferType",
    "TransferStatus",
]
