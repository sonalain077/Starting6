"""
Modèle SQLAlchemy pour la table League (Ligue)

Une ligue peut être:
- SOLO: Publique, tout le monde joue ensemble, pas de limite de joueurs uniques
- PRIVATE: Privée, 8-12 joueurs, chaque joueur NBA ne peut appartenir qu'à 1 équipe
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class LeagueType(enum.Enum):
    """
    Types de ligues disponibles
    
    SOLO: Ligue publique globale
        - Transferts libres à tout moment
        - Joueurs non-uniques (plusieurs équipes peuvent avoir le même joueur)
        - Premier arrivé, premier servi
        - Cooldown 7 jours après avoir viré un joueur
        - Limite: 2 transferts / semaine
    
    PRIVATE: Ligue privée compétitive
        - 8 à 12 joueurs maximum
        - Joueurs uniques (1 joueur NBA = 1 seule équipe)
        - Transferts uniquement le lundi (waiver system)
        - Attribution par waiver priority (ordre inverse du classement)
        - Cooldown 7 jours
        - Limite: 2 transferts / semaine
        - Roster lock du mardi au dimanche
    """
    SOLO = "SOLO"
    PRIVATE = "PRIVATE"


class League(Base):
    """
    Modèle League - Représente une ligue de fantasy basketball
    
    Attributs:
        id: Identifiant unique
        name: Nom de la ligue
        type: Type de ligue (SOLO ou PRIVATE)
        commissioner_id: ID de l'utilisateur créateur (pour PRIVATE uniquement)
        max_teams: Nombre maximum d'équipes (8-12 pour PRIVATE, illimité pour SOLO)
        salary_cap: Plafond salarial (par défaut 60M$)
        is_active: La ligue est-elle active?
        start_date: Date de début de la saison
        end_date: Date de fin de la saison
        date_creation: Date de création de la ligue
    
    Relations:
        commissioner: Utilisateur qui a créé la ligue (commissaire)
        teams: Liste des équipes dans cette ligue
    """
    
    __tablename__ = "leagues"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # Nom de la ligue
    name = Column(
        String(100),
        nullable=False,
        index=True
    )
    # Exemple: "NBA Fantasy 2025", "Ligue entre potes", "SOLO Global League"
    
    # Type de ligue (SOLO ou PRIVATE)
    type = Column(
        SQLEnum(LeagueType),
        nullable=False,
        default=LeagueType.SOLO
    )
    
    # ID du commissaire (créateur de la ligue)
    # NULL pour SOLO, obligatoire pour PRIVATE
    commissioner_id = Column(
        Integer,
        ForeignKey("utilisateurs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Nombre maximum d'équipes
    # NULL = illimité (pour SOLO), 8-12 pour PRIVATE
    max_teams = Column(
        Integer,
        nullable=True
    )
    
    # Plafond salarial (en dollars)
    # Par défaut: 60 000 000 $ (60M$)
    salary_cap = Column(
        Integer,
        nullable=False,
        default=60_000_000
    )
    
    # La ligue est-elle active?
    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )
    
    # Date de début de saison
    start_date = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Date de fin de saison
    end_date = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Date de création
    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # === RELATIONS ===
    
    # Relation avec le commissaire (utilisateur)
    commissioner = relationship(
        "Utilisateur",
        foreign_keys=[commissioner_id],
        back_populates="leagues_as_commissioner"
    )
    
    # Relation avec les équipes de cette ligue
    teams = relationship(
        "FantasyTeam",
        back_populates="league",
        cascade="all, delete-orphan"
    )
    # cascade="all, delete-orphan" signifie:
    # Si on supprime une ligue, toutes ses équipes sont aussi supprimées
    
    def __repr__(self):
        return f"<League(id={self.id}, name='{self.name}', type={self.type.value})>"
