"""
Agrégation des routes API v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, utilisateurs, joueurs, equipes, scores

api_router = APIRouter()

# Inclusion des différents endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(utilisateurs.router, prefix="/utilisateurs", tags=["Utilisateurs"])
api_router.include_router(joueurs.router, prefix="/joueurs", tags=["Joueurs NBA"])
api_router.include_router(equipes.router, prefix="/equipes", tags=["Équipes Fantasy"])
api_router.include_router(scores.router, prefix="/scores", tags=["Scores"])
