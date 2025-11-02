"""
Modèle SQLAlchemy pour la table PlayerGameScore

Stocke le score fantasy d'un joueur pour un match donné.
Calcule les points selon le système de scoring complexe avec bonus et pénalités.
"""
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlayerGameScore(Base):
    """
    Modèle PlayerGameScore - Score fantasy d'un joueur pour un match
    
    Chaque entrée représente la performance d'un joueur dans un match spécifique.
    Le score est calculé selon le système de points détaillé avec:
    - Points de base (PTS, REB, AST, STL, BLK, TO, PF)
    - Bonus d'efficacité (FG%, 3PT, FT%, AST/TO, STL+BLK, REB)
    - Bonus de performance (Double-Double, Triple-Double, 30+ PTS, etc.)
    - Pénalités (FG% bas, TO élevé, disqualification)
    
    Attributs:
        id: Identifiant unique
        player_id: ID du joueur NBA
        game_date: Date du match
        opponent: Équipe adverse
        
        # Statistiques brutes
        minutes_played: Minutes jouées
        points: Points marqués
        rebounds: Rebonds totaux
        offensive_rebounds: Rebonds offensifs
        defensive_rebounds: Rebonds défensifs
        assists: Passes décisives
        steals: Interceptions
        blocks: Contres
        turnovers: Balles perdues
        personal_fouls: Fautes personnelles
        field_goals_made: Paniers réussis
        field_goals_attempted: Paniers tentés
        three_pointers_made: Paniers à 3 points réussis
        three_pointers_attempted: Paniers à 3 points tentés
        free_throws_made: Lancers francs réussis
        free_throws_attempted: Lancers francs tentés
        
        # Scores calculés
        base_score: Score de base (avant bonus)
        efficiency_bonus: Bonus d'efficacité total
        performance_bonus: Bonus de performance total
        penalty: Pénalités totales
        fantasy_score: Score fantasy FINAL
        
        # Détails du calcul (pour debug et transparence)
        calculation_breakdown: JSON détaillant chaque composant du score
    
    Relations:
        player: Le joueur qui a joué ce match
    """
    
    __tablename__ = "player_game_scores"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # === IDENTIFICATION ===
    
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    game_date = Column(
        Date,
        nullable=False,
        index=True
    )
    # Date du match (sans l'heure)
    
    opponent = Column(
        String(50),
        nullable=True
    )
    # Équipe adverse, exemple: "LAL", "GSW", "BOS"
    
    # === STATISTIQUES BRUTES ===
    
    minutes_played = Column(Integer, nullable=False, default=0)
    
    # Points et rebonds
    points = Column(Integer, nullable=False, default=0)
    rebounds = Column(Integer, nullable=False, default=0)
    offensive_rebounds = Column(Integer, nullable=False, default=0)
    defensive_rebounds = Column(Integer, nullable=False, default=0)
    
    # Passes, défense
    assists = Column(Integer, nullable=False, default=0)
    steals = Column(Integer, nullable=False, default=0)
    blocks = Column(Integer, nullable=False, default=0)
    
    # Erreurs
    turnovers = Column(Integer, nullable=False, default=0)
    personal_fouls = Column(Integer, nullable=False, default=0)
    
    # Tirs au panier
    field_goals_made = Column(Integer, nullable=False, default=0)
    field_goals_attempted = Column(Integer, nullable=False, default=0)
    
    # Tirs à 3 points
    three_pointers_made = Column(Integer, nullable=False, default=0)
    three_pointers_attempted = Column(Integer, nullable=False, default=0)
    
    # Lancers francs
    free_throws_made = Column(Integer, nullable=False, default=0)
    free_throws_attempted = Column(Integer, nullable=False, default=0)
    
    # === SCORES CALCULÉS ===
    
    # Score de base (avant bonus et pénalités)
    base_score = Column(
        Float,
        nullable=False,
        default=0.0
    )
    # Calculé à partir de: PTS, REB, AST, STL, BLK, TO, PF
    
    # Bonus d'efficacité
    efficiency_bonus = Column(
        Float,
        nullable=False,
        default=0.0
    )
    # Total des bonus: FG% ≥60%, 3PT ≥3, FT% 100%, AST/TO ≥3:1, STL+BLK ≥4, REB ≥12
    
    # Bonus de performance
    performance_bonus = Column(
        Float,
        nullable=False,
        default=0.0
    )
    # Total des bonus: Double-Double, Triple-Double, 30+ PTS, 15+ AST, Match parfait
    
    # Pénalités
    penalty = Column(
        Float,
        nullable=False,
        default=0.0
    )
    # Total des pénalités: FG% <30%, ≥5 TO, 6 fautes (disqualifié)
    
    # SCORE FANTASY FINAL
    fantasy_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True
    )
    # Formule: base_score + efficiency_bonus + performance_bonus - penalty
    
    # === DÉTAILS DU CALCUL (JSON) ===
    
    calculation_breakdown = Column(
        JSON,
        nullable=True
    )
    # Exemple de structure:
    # {
    #     "base": {
    #         "points": 25.0,
    #         "rebounds": 9.6,
    #         "assists": 12.0,
    #         "steals": 6.0,
    #         "blocks": 0.0,
    #         "turnovers": -3.0,
    #         "fouls": -2.0
    #     },
    #     "efficiency": {
    #         "fg_percentage": 3.0,
    #         "three_pointers": 2.0,
    #         "ast_to_ratio": 3.0
    #     },
    #     "performance": {
    #         "double_double": 5.0,
    #         "thirty_plus_points": 3.0
    #     },
    #     "penalty": {
    #         "high_turnovers": -2.0
    #     },
    #     "final": 52.6
    # }
    
    # === RELATIONS ===
    
    player = relationship(
        "Player",
        back_populates="game_scores"
    )
    
    # === CONTRAINTES ===
    
    # Un joueur ne peut avoir qu'un seul score par match
    __table_args__ = (
        UniqueConstraint('player_id', 'game_date', name='uq_player_game_date'),
    )
    
    def __repr__(self):
        return f"<PlayerGameScore(player_id={self.player_id}, date={self.game_date}, score={self.fantasy_score:.1f})>"
