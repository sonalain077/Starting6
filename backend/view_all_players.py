"""
Script pour afficher TOUS les joueurs de la base de données
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.player import Player

def view_all_players():
    db: Session = SessionLocal()
    
    try:
        # Récupérer tous les joueurs
        players = db.query(Player).order_by(Player.full_name).all()
        
        print("=" * 120)
        print(f"📊 BASE DE DONNÉES COMPLÈTE - {len(players)} JOUEURS SAISON 2025-2026")
        print("=" * 120)
        print()
        
        # Grouper par équipe
        teams = {}
        for player in players:
            team = player.team_abbreviation or "UNK"
            if team not in teams:
                teams[team] = []
            teams[team].append(player)
        
        # Afficher par équipe
        for team in sorted(teams.keys()):
            team_players = teams[team]
            print(f"\n🏀 {team} ({len(team_players)} joueurs)")
            print("-" * 120)
            print(f"{'Nom'.ljust(30)} {'Poste'.ljust(8)} {'ID API'.ljust(12)} {'Salaire'.ljust(15)} {'Active'}")
            print("-" * 120)
            
            for player in sorted(team_players, key=lambda p: p.full_name):
                name = player.full_name[:28]
                position = str(player.position.value) if hasattr(player.position, 'value') else str(player.position)
                api_id = str(player.external_api_id)
                salary = f"${player.fantasy_cost:,.0f}"
                active = "✅" if player.is_active else "❌"
                
                print(f"{name.ljust(30)} {position.ljust(8)} {api_id.ljust(12)} {salary.ljust(15)} {active}")
        
        print("\n" + "=" * 120)
        print(f"📊 RÉSUMÉ")
        print("=" * 120)
        print(f"Total joueurs : {len(players)}")
        print(f"Équipes : {len(teams)}")
        
        # Distribution par position
        positions = {}
        for player in players:
            pos = str(player.position.value) if hasattr(player.position, 'value') else str(player.position)
            positions[pos] = positions.get(pos, 0) + 1
        
        print("\nDistribution par position :")
        for pos in sorted(positions.keys()):
            count = positions[pos]
            percentage = (count / len(players)) * 100
            print(f"  {pos}: {count} joueurs ({percentage:.1f}%)")
        
        print("=" * 120)
        
    finally:
        db.close()


if __name__ == "__main__":
    view_all_players()
