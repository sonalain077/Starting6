"""
Modèle SQLAlchemy pour la table Utilisateur

Ce fichier définit la structure de la table `utilisateurs` dans PostgreSQL.
Chaque classe = 1 table, chaque attribut = 1 colonne.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Utilisateur(Base):
    """
    Modèle Utilisateur - Représente un joueur de la fantasy league
    
    Attributs:
        id: Identifiant unique (clé primaire)
        nom_utilisateur: Nom d'utilisateur unique
        mot_de_passe_hash: Mot de passe hashé (JAMAIS en clair!)
        date_creation: Date de création du compte
    
    Relations:
        equipe: L'équipe fantasy de cet utilisateur (sera ajoutée plus tard)
    """
    
    # Nom de la table dans PostgreSQL
    __tablename__ = "utilisateurs"
    
    # === COLONNES DE LA TABLE ===
    
    # ID - Clé primaire (auto-incrémentée)
    id = Column(
        Integer,           # Type: nombre entier
        primary_key=True,  # C'est la clé primaire
        index=True,        # Créer un index pour accélérer les recherches
        autoincrement=True # PostgreSQL incrémente automatiquement
    )
    
    # Nom d'utilisateur - Unique et obligatoire
    nom_utilisateur = Column(
        String(50),        # Type: texte de maximum 50 caractères
        unique=True,       # Deux utilisateurs ne peuvent pas avoir le même nom
        nullable=False,    # Obligatoire (ne peut pas être NULL)
        index=True         # Index pour rechercher rapidement par nom
    )
    
    # Mot de passe hashé - Obligatoire
    mot_de_passe_hash = Column(
        String(255),       # Type: texte (le hash est long)
        nullable=False     # Obligatoire
    )
    # ⚠️ IMPORTANT: On ne stocke JAMAIS le mot de passe en clair!
    # On stocke un "hash" (version cryptée irréversible)
    
    # Date de création - Automatique
    date_creation = Column(
        DateTime(timezone=True),  # Type: date et heure avec timezone
        server_default=func.now(), # PostgreSQL met la date actuelle automatiquement
        nullable=False
    )
    
    # Statut administrateur - Par défaut False
    is_admin = Column(
        Boolean,               # Type: booléen (True/False)
        default=False,         # Par défaut, les utilisateurs ne sont pas admin
        nullable=False,        # Obligatoire
        server_default='false' # Valeur par défaut côté PostgreSQL
    )
    
    # === RELATIONS ===
    
    # Ligues créées par cet utilisateur (en tant que commissaire)
    leagues_as_commissioner = relationship(
        "League",
        foreign_keys="League.commissioner_id",
        back_populates="commissioner"
    )
    # Relation 1-to-many: Un utilisateur peut créer plusieurs ligues privées
    
    # Équipes de cet utilisateur
    fantasy_teams = relationship(
        "FantasyTeam",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    # Relation 1-to-many: Un utilisateur peut avoir plusieurs équipes (une par ligue)
    
    def __repr__(self):
        """
        Représentation lisible de l'objet pour le debug
        
        Exemple:
            >>> user = Utilisateur(nom_utilisateur="alice")
            >>> print(user)
            <Utilisateur(id=1, nom='alice')>
        """
        return f"<Utilisateur(id={self.id}, nom='{self.nom_utilisateur}')>"
