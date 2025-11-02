"""
Modèle SQLAlchemy pour la table FantasyTeamScore

Stocke le score total d'une équipe fantasy pour un jour donné.
Le score d'une équipe = somme des scores de ses 6 joueurs ce jour-là.
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class FantasyTeamScore(Base):
    """
    Modèle FantasyTeamScore - Score quotidien d'une équipe fantasy
    
    Chaque jour où des matchs NBA ont lieu, le worker calcule:
    1. Le score de chaque joueur NBA (PlayerGameScore)
    2. Le score de chaque équipe fantasy (somme des scores de ses 6 joueurs)
    3. Met à jour le classement
    
    Exemple:
    - Date: 2025-01-15
    - Équipe "Les Monstars" a joué avec:
      * LeBron (PG): 45.2 points
      * Curry (SG): 38.7 points
      * Durant (SF): 0 points (n'a pas joué)
      * Giannis (PF): 52.1 points
      * Jokic (C): 48.3 points
      * Embiid (UTIL): 41.9 points
    - Score total du jour: 226.2 points
    
    Attributs:
        id: Identifiant unique
        fantasy_team_id: ID de l'équipe fantasy
        score_date: Date du score
        total_score: Score total du jour (somme des 6 joueurs)
        players_who_played: Nombre de joueurs qui ont joué ce jour
        details: JSON avec le détail de chaque joueur
    
    Relations:
        fantasy_team: L'équipe fantasy
    """
    
    __tablename__ = "fantasy_team_scores"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # ID de l'équipe fantasy
    fantasy_team_id = Column(
        Integer,
        ForeignKey("fantasy_teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Date du score
    score_date = Column(
        Date,
        nullable=False,
        index=True
    )
    
    # Score total du jour
    total_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True
    )
    # Somme des scores des 6 joueurs
    
    # Nombre de joueurs qui ont effectivement joué ce jour
    players_who_played = Column(
        Integer,
        nullable=False,
        default=0
    )
    # Entre 0 et 6
    # Exemple: Si seulement 3 joueurs avaient un match NBA ce jour, players_who_played = 3
    
    # === RELATIONS ===
    
    fantasy_team = relationship(
        "FantasyTeam",
        back_populates="daily_scores"
    )
    
    # === CONTRAINTES ===
    
    # Une équipe ne peut avoir qu'un seul score par jour
    __table_args__ = (
        UniqueConstraint('fantasy_team_id', 'score_date', name='uq_team_score_date'),
    )
    
    def __repr__(self):
        return f"<FantasyTeamScore(team_id={self.fantasy_team_id}, date={self.score_date}, score={self.total_score:.1f})>"
