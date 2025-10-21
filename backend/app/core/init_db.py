"""
Script d'initialisation de la base de données
Crée toutes les tables définies dans les modèles SQLAlchemy
"""
from app.core.database import engine, Base
from app.models.utilisateur import Utilisateur


def init_db():
    """
    Crée toutes les tables dans PostgreSQL
    """
    print("🔨 Création de la table utilisateurs...")
    
    # Cette ligne magique crée TOUTES les tables définies dans Base
    Base.metadata.create_all(bind=engine)
    
    print("✅ Table 'utilisateurs' créée avec succès!")
    
    # Vérifier que la table a bien été créée
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Tables présentes en base de données:")
    for table in tables:
        print(f"   - {table}")


if __name__ == "__main__":
    init_db()
