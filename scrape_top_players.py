"""
Scrape les 25 meilleurs joueurs de la semaine dernière (28 Oct - 3 Nov 2025)
Utilise nba_api pour récupérer les vraies stats NBA
"""
import sys
sys.path.append('backend')

from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import players as nba_players
from app.core.database import SessionLocal
from app.models.player import Player, Position
import time

def get_top_performers_last_week():
    """
    Récupère les 25 meilleurs performeurs de la semaine dernière
    """
    print("🏀 Récupération des top performeurs de la semaine dernière...")
    print("📅 Période : 28 Oct - 3 Nov 2025\n")
    
    try:
        # Paramètres pour la saison 2024-25
        season = "2024-25"
        season_type = "Regular Season"
        
        # Récupérer les stats des joueurs sur les 7 derniers jours
        print("⏳ Requête vers stats.nba.com...")
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            season_type_all_star=season_type,
            per_mode_detailed="PerGame",
            last_n_games=7,  # 7 derniers matchs
            measure_type_detailed_defense="Base"
        )
        
        df = stats.get_data_frames()[0]
        print(f"✅ {len(df)} joueurs récupérés")
        
        # Calculer un score fantasy approximatif pour trier
        df['FANTASY_SCORE'] = (
            df['PTS'] * 1.0 +
            df['REB'] * 1.2 +
            df['AST'] * 1.5 +
            df['STL'] * 3.0 +
            df['BLK'] * 3.0 -
            df['TOV'] * 1.5
        )
        
        # Trier par score fantasy décroissant
        df = df.sort_values('FANTASY_SCORE', ascending=False)
        
        # Prendre les 25 meilleurs
        top_25 = df.head(25)
        
        print("\n🏆 TOP 25 PERFORMEURS DE LA SEMAINE :\n")
        
        # Récupérer la liste complète des joueurs NBA (pour mapping)
        all_nba_players = nba_players.get_players()
        player_dict = {p['id']: p for p in all_nba_players}
        
        db = SessionLocal()
        
        # Supprimer les anciens joueurs
        deleted = db.query(Player).delete()
        db.commit()
        print(f"🗑️  {deleted} anciens joueurs supprimés\n")
        
        inserted_players = []
        
        for idx, row in top_25.iterrows():
            player_id = row['PLAYER_ID']
            player_name = row['PLAYER_NAME']
            
            # Récupérer la vraie position depuis les données statiques
            player_info = player_dict.get(player_id, {})
            position_raw = player_info.get('position', 'G')
            
            # Mapper la position selon les postes NBA
            position_map = {
                'Guard': Position.SG,
                'Forward': Position.SF,
                'Center': Position.C,
                'Guard-Forward': Position.SG,
                'Forward-Guard': Position.SF,
                'Forward-Center': Position.PF,
                'Center-Forward': Position.C,
                'G': Position.SG,
                'F': Position.SF,
                'C': Position.C,
                'G-F': Position.SG,
                'F-G': Position.SF,
                'F-C': Position.PF,
                'C-F': Position.C,
            }
            
            # Affiner selon le nom du joueur (mapping manuel pour les stars connues)
            name_position_map = {
                'Giannis Antetokounmpo': Position.PF,
                'Nikola Jokić': Position.C,
                'Luka Dončić': Position.PG,
                'Shai Gilgeous-Alexander': Position.PG,
                'James Harden': Position.PG,
                'Trae Young': Position.PG,
                'Tyrese Haliburton': Position.PG,
                'Cade Cunningham': Position.PG,
                'Anthony Davis': Position.C,
                'Rudy Gobert': Position.C,
                'Karl-Anthony Towns': Position.C,
                'Domantas Sabonis': Position.C,
                'Bam Adebayo': Position.C,
                'Ivica Zubac': Position.C,
                'Nikola Vučević': Position.C,
                'Anthony Edwards': Position.SG,
                'Donovan Mitchell': Position.SG,
                'Kawhi Leonard': Position.SF,
                'Jayson Tatum': Position.SF,
                'Paolo Banchero': Position.PF,
                'Evan Mobley': Position.C,
            }
            
            position = name_position_map.get(player_name, position_map.get(position_raw, Position.SG))
            
            # Extraire prénom et nom
            name_parts = player_name.split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else player_name
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Calculer le salaire fantasy basé sur les performances
            avg_score = row['FANTASY_SCORE']
            fantasy_cost = max(2_000_000, min(18_000_000, (avg_score / 5) * 1_000_000))
            
            # Créer le joueur
            new_player = Player(
                external_api_id=player_id,
                first_name=first_name,
                last_name=last_name,
                full_name=player_name,
                position=position,
                team=row['TEAM_ABBREVIATION'],
                team_abbreviation=row['TEAM_ABBREVIATION'],
                fantasy_cost=int(fantasy_cost),
                avg_fantasy_score_last_15=round(avg_score, 1),
                games_played_last_20=int(row['GP']),
                is_active=True
            )
            
            db.add(new_player)
            inserted_players.append({
                'rank': len(inserted_players) + 1,
                'name': player_name,
                'team': row['TEAM_ABBREVIATION'],
                'position': position.value,
                'pts': row['PTS'],
                'reb': row['REB'],
                'ast': row['AST'],
                'fantasy_score': round(avg_score, 1),
                'salary': fantasy_cost
            })
            
            print(f"{len(inserted_players):2d}. {player_name:25s} ({row['TEAM_ABBREVIATION']}) - "
                  f"{position.value} | "
                  f"PTS:{row['PTS']:5.1f} REB:{row['REB']:4.1f} AST:{row['AST']:4.1f} | "
                  f"Fantasy:{avg_score:5.1f} | "
                  f"${fantasy_cost:,.0f}")
            
            # Pause pour éviter le rate limiting
            time.sleep(0.1)
        
        db.commit()
        db.close()
        
        print(f"\n✅ {len(inserted_players)} joueurs insérés avec succès !")
        
        # Statistiques
        print("\n📊 Répartition par équipe :")
        teams = {}
        for p in inserted_players:
            teams[p['team']] = teams.get(p['team'], 0) + 1
        
        for team, count in sorted(teams.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {team}: {count} joueurs")
        
        print("\n📊 Répartition par poste :")
        positions = {}
        for p in inserted_players:
            positions[p['position']] = positions.get(p['position'], 0) + 1
        
        for pos, count in sorted(positions.items()):
            print(f"   {pos}: {count} joueurs")
        
        print("\n💰 Top 5 salaires :")
        for p in sorted(inserted_players, key=lambda x: x['salary'], reverse=True)[:5]:
            print(f"   {p['name']:25s} : ${p['salary']:,.0f}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("🏀 NBA FANTASY LEAGUE - SCRAPER DES TOP PERFORMEURS")
    print("=" * 80)
    print()
    
    get_top_performers_last_week()
