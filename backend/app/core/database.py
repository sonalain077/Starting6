"""
Configuration de la base de données SQLAlchemy

Ce fichier crée la connexion à PostgreSQL et fournit:
- engine: Le moteur de connexion à la BDD
- SessionLocal: Pour créer des sessions de BDD
- Base: La classe de base pour tous nos modèles
- get_db(): Fonction pour obtenir une session BDD dans FastAPI
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Création de l'engine SQLAlchemy
# C'est le "moteur" qui gère la connexion à PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Vérifie que la connexion est vivante avant de l'utiliser
    echo=True  # Affiche les requêtes SQL dans la console
)

# SessionLocal est une "fabrique" de sessions de base de données
# Chaque session = une conversation avec la BDD
SessionLocal = sessionmaker(
    autocommit=False,  # On ne commit pas automatiquement
    autoflush=False,   # On ne flush pas automatiquement
    bind=engine        # On lie au moteur créé ci-dessus
)

# Base est la classe parente de tous nos modèles
# Tous nos modèles (User, Player, etc.) vont hériter de Base
Base = declarative_base()


def get_db():
    """
    Générateur de session de base de données
    
    Cette fonction est utilisée comme "dependency" dans FastAPI.
    Elle crée une session, la donne à ton endpoint, puis la ferme.
    
    Exemple d'utilisation:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            # db est une session active ici
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db  # Donne la session à celui qui appelle
    finally:
        db.close()  # Ferme toujours la session à la fin
