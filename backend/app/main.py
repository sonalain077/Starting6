"""
Point d'entrée de l'API FastAPI
NBA Fantasy League - Starting Six
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import auth  

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