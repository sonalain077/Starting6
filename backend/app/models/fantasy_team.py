"""
Modèle SQLAlchemy pour la table FantasyTeam (Équipe Fantasy)

Représente l'équipe d'un utilisateur dans une ligue.
Chaque équipe a 6 joueurs (PG, SG, SF, PF, C, UTIL) et un salary cap de 60M$.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FantasyTeam(Base):
    """
    Modèle FantasyTeam - Représente l'équipe fantasy d'un utilisateur
    
    Attributs:
        id: Identifiant unique
        name: Nom de l'équipe
        owner_id: ID de l'utilisateur propriétaire
        league_id: ID de la ligue dans laquelle joue cette équipe
        salary_cap_used: Somme des salaires des joueurs actuels
        waiver_priority: Priorité dans le système de waiver (PRIVATE leagues)
        transfers_this_week: Nombre de transferts effectués cette semaine
        total_score: Score total accumulé depuis le début de la saison
        rank: Classement actuel dans la ligue
        date_creation: Date de création de l'équipe
        last_updated: Dernière mise à jour
    
    Relations:
        owner: Utilisateur propriétaire
        league: Ligue dans laquelle joue cette équipe
        players: Liste des joueurs de cette équipe (via FantasyTeamPlayer)
        transfers: Historique des transferts
        daily_scores: Scores quotidiens de l'équipe
    
    Contraintes:
        - Un utilisateur ne peut avoir qu'une seule équipe par ligue
        - Salary cap: Maximum 60M$
        - Roster: 6 joueurs (1 PG, 1 SG, 1 SF, 1 PF, 1 C, 1 UTIL)
        - Maximum 2 transferts par semaine
    """
    
    __tablename__ = "fantasy_teams"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # Nom de l'équipe
    name = Column(
        String(100),
        nullable=False
    )
    # Exemple: "Les Monstars", "Dream Team 2025", "Alain's Squad"
    
    # === RELATIONS AVEC UTILISATEUR ET LIGUE ===
    
    # ID du propriétaire (utilisateur)
    owner_id = Column(
        Integer,
        ForeignKey("utilisateurs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    # CASCADE: Si l'utilisateur est supprimé, son équipe aussi
    
    # ID de la ligue
    league_id = Column(
        Integer,
        ForeignKey("leagues.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    # CASCADE: Si la ligue est supprimée, toutes ses équipes aussi
    
    # === GESTION DU SALARY CAP ===
    
    # Montant total utilisé du salary cap
    salary_cap_used = Column(
        Integer,
        nullable=False,
        default=0
    )
    # Max: 60 000 000 (60M$)
    # Calculé automatiquement: somme des fantasy_cost de tous les joueurs
    
    # === SYSTÈME DE TRANSFERTS ===
    
    # Priorité waiver (pour PRIVATE leagues)
    waiver_priority = Column(
        Integer,
        nullable=True,
        default=None
    )
    # Ordre inverse du classement: dernier = priorité 1, premier = priorité N
    # NULL pour SOLO leagues (pas de waiver system)
    
    # Nombre de transferts effectués cette semaine
    transfers_this_week = Column(
        Integer,
        nullable=False,
        default=0
    )
    # Maximum: 2 transferts par semaine
    # Reset chaque lundi à 00h00
    
    # === STATISTIQUES ===
    
    # Score total accumulé
    total_score = Column(
        Integer,
        nullable=False,
        default=0,
        index=True
    )
    # Somme de tous les scores quotidiens depuis le début de la saison
    
    # Classement actuel
    rank = Column(
        Integer,
        nullable=True,
        index=True
    )
    # Position dans le leaderboard de la ligue
    
    # === MÉTADONNÉES ===
    
    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # === RELATIONS ===
    
    # Propriétaire de l'équipe
    owner = relationship(
        "Utilisateur",
        back_populates="fantasy_teams"
    )
    
    # Ligue de l'équipe
    league = relationship(
        "League",
        back_populates="teams"
    )
    
    # Joueurs de l'équipe (table intermédiaire)
    players = relationship(
        "FantasyTeamPlayer",
        back_populates="fantasy_team",
        cascade="all, delete-orphan"
    )
    # Liste des 6 joueurs avec leur poste dans l'équipe
    
    # Historique des transferts
    transfers = relationship(
        "Transfer",
        back_populates="fantasy_team",
        cascade="all, delete-orphan"
    )
    
    # Scores quotidiens
    daily_scores = relationship(
        "FantasyTeamScore",
        back_populates="fantasy_team",
        cascade="all, delete-orphan"
    )
    
    # === CONTRAINTES ===
    
    # Un utilisateur ne peut avoir qu'une seule équipe par ligue
    __table_args__ = (
        UniqueConstraint('owner_id', 'league_id', name='uq_owner_league'),
    )
    
    def __repr__(self):
        return f"<FantasyTeam(id={self.id}, name='{self.name}', cap_used=${self.salary_cap_used:,}, score={self.total_score})>"
