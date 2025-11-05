"""
Script pour insérer des joueurs sample dans la base de données
Pour tester les endpoints Player avant l'intégration de l'API externe
"""
import sys
sys.path.append('backend')

from app.core.database import SessionLocal
from app.models.player import Player, Position

def seed_players():
    """Insère des joueurs NBA réalistes dans la base"""
    db = SessionLocal()
    
    try:
        # Vérifier si des joueurs existent déjà
        existing_count = db.query(Player).count()
        if existing_count > 0:
            print(f"⚠️ {existing_count} joueurs existent déjà dans la base.")
            response = input("Voulez-vous les supprimer et réinsérer ? (y/n) : ")
            if response.lower() != 'y':
                print("❌ Annulation.")
                return
            
            # Supprimer tous les joueurs existants
            db.query(Player).delete()
            db.commit()
            print("🗑️ Joueurs supprimés.")
        
        # Liste de joueurs NBA réalistes avec salaires fantasy
        # Données mises à jour : Novembre 2025
        sample_players = [
            # Superstars (14M$ - 18M$)
            Player(
                external_api_id=2544,
                first_name="LeBron",
                last_name="James",
                full_name="LeBron James",
                position=Position.SF,
                team="Los Angeles Lakers",
                team_abbreviation="LAL",
                fantasy_cost=15_800_000,
                avg_fantasy_score_last_15=46.2,
                games_played_last_20=16,
                is_active=True
            ),
            Player(
                external_api_id=201939,
                first_name="Stephen",
                last_name="Curry",
                full_name="Stephen Curry",
                position=Position.PG,
                team="Golden State Warriors",
                team_abbreviation="GSW",
                fantasy_cost=16_200_000,
                avg_fantasy_score_last_15=47.8,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=201935,
                first_name="James",
                last_name="Harden",
                full_name="James Harden",
                position=Position.SG,
                team="LA Clippers",
                team_abbreviation="LAC",
                fantasy_cost=13_900_000,
                avg_fantasy_score_last_15=41.3,
                games_played_last_20=17,
                is_active=True
            ),
            Player(
                external_api_id=203507,
                first_name="Giannis",
                last_name="Antetokounmpo",
                full_name="Giannis Antetokounmpo",
                position=Position.PF,
                team="Milwaukee Bucks",
                team_abbreviation="MIL",
                fantasy_cost=17_900_000,
                avg_fantasy_score_last_15=55.4,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=203954,
                first_name="Joel",
                last_name="Embiid",
                full_name="Joel Embiid",
                position=Position.C,
                team="Philadelphia 76ers",
                team_abbreviation="PHI",
                fantasy_cost=16_800_000,
                avg_fantasy_score_last_15=52.1,
                games_played_last_20=14,
                is_active=True
            ),
            
            # All-Stars (10M$ - 14M$)
            Player(
                external_api_id=1628369,
                first_name="Luka",
                last_name="Doncic",
                full_name="Luka Doncic",
                position=Position.PG,
                team="Los Angeles Lakers",  # ⚠️ TRADE 2024-2025
                team_abbreviation="LAL",
                fantasy_cost=17_200_000,
                avg_fantasy_score_last_15=53.8,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=203999,
                first_name="Nikola",
                last_name="Jokic",
                full_name="Nikola Jokic",
                position=Position.C,
                team="Denver Nuggets",
                team_abbreviation="DEN",
                fantasy_cost=18_000_000,
                avg_fantasy_score_last_15=59.2,
                games_played_last_20=20,
                is_active=True
            ),
            Player(
                external_api_id=1628983,
                first_name="Shai",
                last_name="Gilgeous-Alexander",
                full_name="Shai Gilgeous-Alexander",
                position=Position.PG,
                team="Oklahoma City Thunder",
                team_abbreviation="OKC",
                fantasy_cost=16_400_000,
                avg_fantasy_score_last_15=50.1,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=1629029,
                first_name="Jayson",
                last_name="Tatum",
                full_name="Jayson Tatum",
                position=Position.SF,
                team="Boston Celtics",
                team_abbreviation="BOS",
                fantasy_cost=15_600_000,
                avg_fantasy_score_last_15=46.8,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=1629630,
                first_name="Anthony",
                last_name="Edwards",
                full_name="Anthony Edwards",
                position=Position.SG,
                team="Minnesota Timberwolves",
                team_abbreviation="MIN",
                fantasy_cost=14_800_000,
                avg_fantasy_score_last_15=44.9,
                games_played_last_20=19,
                is_active=True
            ),
            
            # Starters solides (6M$ - 10M$)
            Player(
                external_api_id=1630162,
                first_name="Tyrese",
                last_name="Haliburton",
                full_name="Tyrese Haliburton",
                position=Position.PG,
                team="Indiana Pacers",
                team_abbreviation="IND",
                fantasy_cost=11_200_000,
                avg_fantasy_score_last_15=38.4,
                games_played_last_20=16,
                is_active=True
            ),
            Player(
                external_api_id=1630163,
                first_name="LaMelo",
                last_name="Ball",
                full_name="LaMelo Ball",
                position=Position.PG,
                team="Charlotte Hornets",
                team_abbreviation="CHA",
                fantasy_cost=10_800_000,
                avg_fantasy_score_last_15=36.7,
                games_played_last_20=14,
                is_active=True
            ),
            Player(
                external_api_id=203081,
                first_name="Damian",
                last_name="Lillard",
                full_name="Damian Lillard",
                position=Position.PG,
                team="Milwaukee Bucks",
                team_abbreviation="MIL",
                fantasy_cost=14_200_000,
                avg_fantasy_score_last_15=43.2,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=203076,
                first_name="Anthony",
                last_name="Davis",
                full_name="Anthony Davis",
                position=Position.PF,
                team="Los Angeles Lakers",
                team_abbreviation="LAL",
                fantasy_cost=16_600_000,
                avg_fantasy_score_last_15=51.3,
                games_played_last_20=17,
                is_active=True
            ),
            Player(
                external_api_id=201142,
                first_name="Kevin",
                last_name="Durant",
                full_name="Kevin Durant",
                position=Position.SF,
                team="Phoenix Suns",
                team_abbreviation="PHX",
                fantasy_cost=16_100_000,
                avg_fantasy_score_last_15=48.7,
                games_played_last_20=18,
                is_active=True
            ),
            
            # Starters/Role players (6M$ - 12M$)
            Player(
                external_api_id=1627749,
                first_name="Jaren",
                last_name="Jackson Jr.",
                full_name="Jaren Jackson Jr.",
                position=Position.PF,
                team="Memphis Grizzlies",
                team_abbreviation="MEM",
                fantasy_cost=10_100_000,
                avg_fantasy_score_last_15=36.4,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=1627759,
                first_name="John",
                last_name="Collins",
                full_name="John Collins",
                position=Position.PF,
                team="Utah Jazz",
                team_abbreviation="UTA",
                fantasy_cost=8_600_000,
                avg_fantasy_score_last_15=32.1,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=203897,
                first_name="Rudy",
                last_name="Gobert",
                full_name="Rudy Gobert",
                position=Position.C,
                team="Minnesota Timberwolves",
                team_abbreviation="MIN",
                fantasy_cost=10_800_000,
                avg_fantasy_score_last_15=37.2,
                games_played_last_20=20,
                is_active=True
            ),
            Player(
                external_api_id=1626178,
                first_name="Pascal",
                last_name="Siakam",
                full_name="Pascal Siakam",
                position=Position.PF,
                team="Indiana Pacers",
                team_abbreviation="IND",
                fantasy_cost=12_400_000,
                avg_fantasy_score_last_15=41.2,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=1630567,
                first_name="Victor",
                last_name="Wembanyama",
                full_name="Victor Wembanyama",
                position=Position.C,
                team="San Antonio Spurs",
                team_abbreviation="SAS",
                fantasy_cost=15_200_000,
                avg_fantasy_score_last_15=48.6,
                games_played_last_20=17,
                is_active=True
            ),
            
            # Role players (6M$ - 10M$)
            Player(
                external_api_id=1629011,
                first_name="Jordan",
                last_name="Poole",
                full_name="Jordan Poole",
                position=Position.SG,
                team="Washington Wizards",
                team_abbreviation="WAS",
                fantasy_cost=7_100_000,
                avg_fantasy_score_last_15=27.8,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=1628386,
                first_name="Wendell",
                last_name="Carter Jr.",
                full_name="Wendell Carter Jr.",
                position=Position.C,
                team="Orlando Magic",
                team_abbreviation="ORL",
                fantasy_cost=8_200_000,
                avg_fantasy_score_last_15=30.4,
                games_played_last_20=18,
                is_active=True
            ),
            Player(
                external_api_id=1630173,
                first_name="Cole",
                last_name="Anthony",
                full_name="Cole Anthony",
                position=Position.PG,
                team="Orlando Magic",
                team_abbreviation="ORL",
                fantasy_cost=6_300_000,
                avg_fantasy_score_last_15=25.2,
                games_played_last_20=16,
                is_active=True
            ),
            Player(
                external_api_id=1630244,
                first_name="Jalen",
                last_name="Green",
                full_name="Jalen Green",
                position=Position.SG,
                team="Houston Rockets",
                team_abbreviation="HOU",
                fantasy_cost=10_200_000,
                avg_fantasy_score_last_15=36.8,
                games_played_last_20=19,
                is_active=True
            ),
            Player(
                external_api_id=1630169,
                first_name="Franz",
                last_name="Wagner",
                full_name="Franz Wagner",
                position=Position.SF,
                team="Orlando Magic",
                team_abbreviation="ORL",
                fantasy_cost=9_400_000,
                avg_fantasy_score_last_15=33.7,
                games_played_last_20=20,
                is_active=True
            ),
            Player(
                external_api_id=1631094,
                first_name="Chet",
                last_name="Holmgren",
                full_name="Chet Holmgren",
                position=Position.C,
                team="Oklahoma City Thunder",
                team_abbreviation="OKC",
                fantasy_cost=11_600_000,
                avg_fantasy_score_last_15=39.4,
                games_played_last_20=18,
                is_active=True
            ),
        ]
        
        # Insérer tous les joueurs
        db.add_all(sample_players)
        db.commit()
        
        print(f"\n✅ {len(sample_players)} joueurs insérés avec succès !")
        print("\n📊 Répartition par poste :")
        for position in Position:
            count = sum(1 for p in sample_players if p.position == position)
            print(f"   - {position.value} : {count} joueurs")
        
        print("\n💰 Répartition par salaire :")
        superstars = sum(1 for p in sample_players if p.fantasy_cost >= 14_000_000)
        allstars = sum(1 for p in sample_players if 10_000_000 <= p.fantasy_cost < 14_000_000)
        starters = sum(1 for p in sample_players if 6_000_000 <= p.fantasy_cost < 10_000_000)
        role_players = sum(1 for p in sample_players if 2_000_000 <= p.fantasy_cost < 6_000_000)
        
        print(f"   - Superstars (14M$+) : {superstars}")
        print(f"   - All-Stars (10M$ - 14M$) : {allstars}")
        print(f"   - Starters (6M$ - 10M$) : {starters}")
        print(f"   - Role players (2M$ - 6M$) : {role_players}")
        
        print("\n🏀 Exemples de joueurs :")
        for p in sample_players[:5]:
            print(f"   - {p.full_name} ({p.position.value}, {p.team_abbreviation}) : ${p.fantasy_cost:,.0f}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏀 Insertion de joueurs sample dans la base...")
    seed_players()
