"""
Point d'entrée de l'API FastAPI
NBA Fantasy League - Starting Six
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import auth, leagues, teams, players, roster, scores, utilisateurs  

# Créer l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour gérer votre équipe de fantasy basketball NBA",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuration CORS (pour permettre les requêtes depuis le frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes d'authentification
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["🔐 Authentification"]
)

# Inclure les routes des utilisateurs
app.include_router(
    utilisateurs.router,
    prefix=f"{settings.API_V1_STR}/utilisateurs",
    tags=["👤 Utilisateurs"]
)

# Inclure les routes des ligues
app.include_router(
    leagues.router,
    prefix=f"{settings.API_V1_STR}/leagues",
    tags=["🏆 Ligues"]
)

# Inclure les routes des équipes fantasy
app.include_router(
    teams.router,
    prefix=f"{settings.API_V1_STR}/teams",
    tags=["🏀 Équipes Fantasy"]
)

# Inclure les routes des joueurs NBA
app.include_router(
    players.router,
    prefix=f"{settings.API_V1_STR}/players",
    tags=["🏀 Joueurs NBA"]
)

# Inclure les routes de gestion du roster (6 joueurs)
app.include_router(
    roster.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["👥 Roster Management"]
)

# Inclure les routes des scores et leaderboards
app.include_router(
    scores.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["📊 Scores & Leaderboard"]
)

# Route de santé (health check)
@app.get("/health", tags=["🏥 Santé"])
def health_check():
    """
    Endpoint pour vérifier que l'API fonctionne
    """
    return {
        "status": "✅ API opérationnelle",
        "project": settings.PROJECT_NAME,
        "database": settings.POSTGRES_DB,
        "host": settings.POSTGRES_HOST
    }

# Route racine
@app.get("/", tags=["🏠 Accueil"])
def root():
    """
    Page d'accueil de l'API
    """
    return {
        "message": "🏀 Bienvenue sur NBA Fantasy League - Starting Six!",
        "docs": "/docs",
        "version": "1.0.0"
    }