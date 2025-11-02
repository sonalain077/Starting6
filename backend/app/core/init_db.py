"""
Script d'initialisation de la base de données
Crée toutes les tables définies dans les modèles SQLAlchemy

Phase 2: Ajout de 7 nouveaux modèles pour le système fantasy complet
"""
from app.core.database import engine, Base

# Import de TOUS les modèles (obligatoire pour que SQLAlchemy les connaisse)
from app.models.utilisateur import Utilisateur
from app.models.league import League, LeagueType
from app.models.player import Player, Position
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer, RosterSlot
from app.models.player_game_score import PlayerGameScore
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.transfer import Transfer, TransferType, TransferStatus


def init_db():
    """
    Crée toutes les tables dans PostgreSQL
    
    Tables créées:
    1. utilisateurs (Phase 1)
    2. leagues (Phase 2)
    3. players (Phase 2)
    4. fantasy_teams (Phase 2)
    5. fantasy_team_players (Phase 2)
    6. player_game_scores (Phase 2)
    7. fantasy_team_scores (Phase 2)
    8. transfers (Phase 2)
    """
    print("🔨 Création de toutes les tables...")
    print("\n📋 Modèles importés:")
    print("   ✅ Utilisateur")
    print("   ✅ League (SOLO/PRIVATE)")
    print("   ✅ Player (joueurs NBA)")
    print("   ✅ FantasyTeam (équipes fantasy)")
    print("   ✅ FantasyTeamPlayer (roster 6 joueurs)")
    print("   ✅ PlayerGameScore (scores quotidiens)")
    print("   ✅ FantasyTeamScore (scores équipe)")
    print("   ✅ Transfer (historique transferts)")
    
    # Cette ligne magique crée TOUTES les tables définies dans Base
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Toutes les tables ont été créées avec succès!")
    
    # Vérifier que toutes les tables ont bien été créées
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Tables créées en base de données ({len(tables)} tables):")
    for table in sorted(tables):
        print(f"   ✓ {table}")
    
    # Vérification complète
    expected_tables = [
        'utilisateurs',
        'leagues', 
        'players',
        'fantasy_teams',
        'fantasy_team_players',
        'player_game_scores',
        'fantasy_team_scores',
        'transfers'
    ]
    
    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n⚠️  ATTENTION: Tables manquantes: {missing}")
    else:
        print(f"\n🎉 Parfait! Toutes les {len(expected_tables)} tables attendues sont créées!")


if __name__ == "__main__":
    init_db()
