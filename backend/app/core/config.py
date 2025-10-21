"""
Configuration de l'application avec Pydantic Settings
Charge les variables depuis le fichier .env
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Trouver le fichier .env à la racine du projet
# backend/app/core/config.py -> remonte de 3 niveaux pour atteindre la racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """
    Configuration centralisée de l'application
    Les valeurs sont chargées depuis les variables d'environnement ou le fichier .env
    """
    
    # ========================================
    # Configuration PostgreSQL
    # ========================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    
    # ========================================
    # Configuration FastAPI
    # ========================================
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NBA Fantasy League"
    
    # ========================================
    # Configuration JWT
    # ========================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ========================================
    # Configuration API Externe
    # ========================================
    BALLDONTLIE_API_KEY: Optional[str] = None
    
    # ========================================
    # Configuration Worker
    # ========================================
    UPDATE_SCHEDULE_HOUR: int = 3
    UPDATE_SCHEDULE_TIMEZONE: str = "America/New_York"
    
    # ========================================
    # Mode Debug
    # ========================================
    DEBUG: bool = True
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construit l'URL de connexion PostgreSQL
        Format: postgresql://user:password@host:port/database
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    class Config:
        # Spécifier explicitement le chemin du fichier .env
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Instancier la configuration (singleton)
settings = Settings()

# Afficher les infos de connexion en mode debug
if settings.DEBUG:
    print(f"🔧 Configuration chargée depuis: {ENV_FILE}")
    print(f"📊 Base de données: {settings.POSTGRES_DB}")
    print(f"🔗 Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")