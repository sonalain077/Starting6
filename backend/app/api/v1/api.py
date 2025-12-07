"""
Agrégation des routes API v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    utilisateurs,
    players,
    teams,
    leagues,
    roster,
    scores
)

api_router = APIRouter()

# Inclusion des différents endpoints (routes en anglais pour le frontend)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(utilisateurs.router, prefix="/users", tags=["Utilisateurs"])
api_router.include_router(players.router, prefix="/players", tags=["Joueurs NBA"])
api_router.include_router(teams.router, prefix="/teams", tags=["Équipes Fantasy"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["Ligues"])
api_router.include_router(roster.router, prefix="/roster", tags=["Roster"])
api_router.include_router(scores.router, prefix="/scores", tags=["Scores"])
