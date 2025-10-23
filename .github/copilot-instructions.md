# Projet Fullstack Data : NBA Fantasy League "Starting Six"

Ce projet est une application web fullstack permettant de gérer une ligue de fantasy basketball basée sur les performances réelles des joueurs de la NBA.  
Le concept unique de **"Starting Six"** impose aux utilisateurs de construire une équipe de 6 joueurs respectant les postes traditionnels du basketball et un plafond salarial (salary cap).

---

## 🚀 Concept du Projet
L'application permet à un utilisateur de s'inscrire, de créer son équipe de rêve en choisissant 6 joueurs de la NBA, et de compétitionner contre d'autres utilisateurs.  
Le score de chaque équipe est calculé quotidiennement en fonction des statistiques réelles des joueurs lors des matchs de la veille.  
Un leaderboard général permet de suivre le classement en temps réel.

---

## ⚙️ Contraintes Stratégiques
**Formation de l'équipe :**
- 1 Meneur (**PG**)
- 1 Arrière (**SG**)
- 1 Ailier (**SF**)
- 1 Ailier Fort (**PF**)
- 1 Pivot (**C**)
- 1 Sixième Homme (**UTIL**, n’importe quel poste)

**Plafond Salarial (Salary Cap) :**
- Chaque utilisateur dispose d’un **budget fixe de 60M$**
- La valeur de chaque joueur est calculée **dynamiquement** selon ses performances fantasy (voir section “Système de Salaire Dynamique”)

---

## 🛠️ Stack Technique
- **Frontend :** Next.js 15 (React + TypeScript)
- **Backend :** Python / FastAPI  
- **Base de Données :** PostgreSQL + SQLAlchemy  
- **Conteneurisation :** Docker & Docker Compose  
- **Authentification :** JWT Tokens  
- **Tests :** Pytest  
- **API Externe :** [balldontlie.io](https://www.balldontlie.io) pour récupérer les stats, joueurs et matchs NBA.

---

## 🏛️ Architecture

### Services Docker
| Service | Rôle |
|----------|------|
| `api` | Backend principal (FastAPI) – Gère les utilisateurs, équipes, transferts, endpoints. |
| `db` | Base PostgreSQL – Stocke joueurs, utilisateurs, équipes, scores, salaires, ligues. |
| `worker` | Script Python de fond – Calcule les scores, met à jour les salaires et le classement. |

---

## 📊 Modèle de Données (SQLAlchemy)
### Principaux Modèles :
- **User** → username, email, password_hash  
- **Player** → id, external_api_id, full_name, position, fantasy_cost  
- **FantasyTeam** → id, user_id, name, league_id, salary_cap_used, waiver_priority  
- **PlayerGameScore** → player_id, game_date, fantasy_score  
- **FantasyTeamScore** → team_id, score_date, total_score  
- **League** → id, name, type ("SOLO"/"PRIVATE"), commissioner_id, max_teams, is_active

---

# 🧠 Logique Métier Clé

## 🧮 Système de Points (Fantasy Scoring Engine)

Chaque joueur accumule des points selon ses performances réelles.  
Le calcul est fait par le **worker** à partir des boxscores NBA récupérés via l’API externe.

### Barème de base
| Statistique | Points | Justification |
|--------------|--------|---------------|
| Point marqué (PTS) | +1.0 | Valeur offensive brute |
| Rebond défensif | +1.2 | Effort défensif utile |
| Rebond offensif | +1.5 | Crée une nouvelle possession |
| Passe décisive (AST) | +1.5 | Impact direct sur le scoring |
| Interception (STL) | +3.0 | Change la possession |
| Contre (BLK) | +3.0 | Défense de haut niveau |
| Balle perdue (TO) | -1.5 | Pénalité de perte de balle |
| Faute personnelle | -0.5 | Sanction de jeu |
| Tir manqué (eff < 40%) | -0.5 | Pénalise les mauvais shooters |

---

### Bonus d’efficacité
| Condition | Bonus |
|------------|--------|
| FG% ≥ 60% (≥10 tentatives) | +3 |
| 3PT ≥ 3 réussis | +2 |
| FT% = 100% (≥4 tentatives) | +1 |
| AST/TO ≥ 3:1 (≥5 assists) | +3 |
| STL + BLK ≥ 4 | +2 |
| REB ≥ 12 | +2 |

---

### Bonus de performance globale
| Réalisation | Bonus |
|--------------|--------|
| Double-Double | +5 |
| Triple-Double | +12 |
| Quadruple-Double | +25 |
| 30+ points marqués | +3 |
| 15+ assists | +3 |
| Match parfait (0 TO, FG% > 70%) | +5 |

---

### Pénalités de performance
| Situation | Pénalité |
|------------|----------|
| FG% < 30% (≥15 tirs) | -3 |
| ≥5 TO dans un match | -2 |
| 6 fautes (disqualifié) | -5 |

---

### Exemple de Calcul
```python
def calculate_fantasy_score(stats: dict) -> float:
    score = 0.0
    score += stats['pts'] * 1.0
    score += stats['reb'] * 1.2
    score += stats['ast'] * 1.5
    score += stats['stl'] * 3.0
    score += stats['blk'] * 3.0
    score -= stats['turnover'] * 1.5
    score -= stats['pf'] * 0.5

    fg_pct = stats['fgm'] / stats['fga'] if stats['fga'] > 0 else 0
    if stats['fga'] >= 10 and fg_pct >= 0.60:
        score += 3
    if stats['fg3m'] >= 3:
        score += 2

    double_stats = sum([
        stats['pts'] >= 10,
        stats['reb'] >= 10,
        stats['ast'] >= 10,
        stats['stl'] >= 10,
        stats['blk'] >= 10,
    ])
    if double_stats == 2:
        score += 5
    elif double_stats == 3:
        score += 12
    elif double_stats >= 4:
        score += 25

    if stats['pts'] >= 30:
        score += 3
    if stats['turnover'] >= 5:
        score -= 2

    return round(score, 1)
```

---

## 💰 Système de Salaire Dynamique

### Objectif :
Faire évoluer la valeur fantasy de chaque joueur selon sa performance réelle, indépendamment de son salaire NBA.

### Fonction de calcul
```python
def calculate_player_salary(player_stats: dict) -> float:
    avg_fantasy_score = player_stats['avg_last_15_games']
    base_salary = (avg_fantasy_score / 5) * 1_000_000

    consistency_factor = 1 - (player_stats['std_dev'] / avg_fantasy_score)
    consistency_bonus = base_salary * consistency_factor * 0.15

    availability_factor = player_stats['games_played_last_20'] / 20
    final_salary = (base_salary + consistency_bonus) * availability_factor

    return max(2_000_000, min(18_000_000, final_salary))
```

### Mise à jour hebdomadaire
```python
def update_all_salaries():
    players = db.query(Player).all()
    for player in players:
        recent_scores = get_recent_fantasy_scores(player.id, limit=15)
        if len(recent_scores) >= 5:
            avg_score = statistics.mean(recent_scores)
            std_dev = statistics.stdev(recent_scores)
            games_played = count_games_last_20_days(player.id)
            new_salary = calculate_player_salary({
                'avg_last_15_games': avg_score,
                'std_dev': std_dev,
                'games_played_last_20': games_played
            })
            player.fantasy_cost = round(new_salary, 2)
    db.commit()
```

---

## 🔄 Système de Transferts & Trades

- **2 transferts maximum / semaine**
- **Cooldown 7 jours** après avoir viré un joueur
- **Transferts poste pour poste** (sauf UTIL)

---

## 🎮 Modes de Jeu

### SOLO LEAGUE
| Élément | Détail |
|----------|--------|
| Type | Public / Global |
| Transferts | Libres à tout moment |
| Attribution | Premier arrivé, premier servi |
| Cooldown | 7 jours |
| Limite | 2 transferts / semaine |
| Joueurs uniques | ❌ Non |
| Classement | Global |
| Style | Accessible, fun, instantané |

### PRIVATE LEAGUE
| Élément | Détail |
|----------|--------|
| Type | Privée (8–12 joueurs) |
| Joueurs uniques | ✅ Oui |
| Transferts | Lundi uniquement (00h–23h59) |
| Attribution | Waiver Priority (ordre inverse du classement) |
| Cooldown | 7 jours |
| Limite | 2 transferts / semaine |
| Salary Cap | 60M$ |
| Roster lock | Mardi → Dimanche |
| Style | Stratégique, compétitif |

---

## 🧩 Contraintes de Roster
| Poste | Description |
|--------|-------------|
| PG | Meneur |
| SG | Arrière |
| SF | Ailier |
| PF | Ailier Fort |
| C | Pivot |
| UTIL | Sixième homme (n’importe quel poste) |

---

## ⚙️ Worker – Pipelines Automatiques

### Tâches principales
1. `update_fantasy_scores()` : calcule les scores journaliers
2. `update_all_salaries()` : ajuste les salaires chaque lundi
3. `process_waiver_claims()` : traite les transferts du lundi (Private League)
4. `update_leaderboards()` : met à jour les classements

---

## ✅ Résumé Global
| Système | Description |
|----------|--------------|
| Scoring | Complexe, basé sur stats réelles et efficacité |
| Salaire | Dynamique, auto-ajusté chaque lundi |
| Cap | 60M$ constant |
| Modes | Solo (libre) & Private (waiver, joueurs uniques) |
| Transferts | 2 max / semaine, 7j cooldown |
| Worker | Centralise calculs & mises à jour |
