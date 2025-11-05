# 🤖 Worker NBA Fantasy - Documentation

## 📖 Vue d'ensemble

Le **Worker** est un service autonome qui s'exécute en arrière-plan 24/7 pour automatiser toutes les tâches critiques de l'application NBA Fantasy League "Starting Six".

Il est basé sur **APScheduler** avec un scheduler asynchrone qui exécute 7 tâches planifiées selon un calendrier précis.

---

## ⏰ Planning d'Exécution

Toutes les heures sont en **Europe/Paris (GMT+1)**.

### Tâches Quotidiennes

| Heure | Tâche | Description |
|-------|-------|-------------|
| **06h00** | `detect_nba_trades` | Détecte les changements d'équipe des joueurs NBA |
| **07h00** | `sync_nba_players` | Synchronise la liste complète des joueurs avec balldontlie.io |
| **08h00** | `fetch_yesterday_boxscores` | Récupère les stats détaillées des matchs de la veille (nba_api) |
| **09h00** | `calculate_yesterday_team_scores` | Calcule le score fantasy de chaque équipe |
| **13h30** | `update_leaderboards` | Met à jour les classements SOLO et PRIVATE |

### Tâches Hebdomadaires (Lundis uniquement)

| Heure | Tâche | Description |
|-------|-------|-------------|
| **10h00** | `update_all_player_salaries` | Recalcule les salaires fantasy selon les 15 dernières perfs |
| **13h00** | `process_waiver_claims` | Traite les demandes de transfert (ligues privées) |

---

## 🎯 Justification de l'Horaire

### Pourquoi 6h du matin ?
Les **matchs NBA West Coast** (LAL, LAC, GSW, etc.) se terminent généralement vers **5h du matin heure de Paris**.

Le worker démarre à **6h** pour laisser le temps aux APIs de mettre à jour leurs données.

### Pourquoi 8h pour les boxscores ?
- Buffer de **3 heures** après la fin du dernier match
- Garantit que **stats.nba.com** et **nba_api** ont synchronisé toutes les statistiques
- Évite les erreurs de données incomplètes

### Pourquoi 10h le lundi pour les salaires ?
- Lundi = début de semaine fantasy
- Permet aux utilisateurs de voir les nouveaux salaires **avant** les premiers matchs du lundi soir
- Laisse le temps de revoir sa stratégie de transfert

### Pourquoi 13h pour les waivers ?
- Les transferts sont validés **avant** que les matchs du lundi soir ne commencent (19h-21h)
- Les utilisateurs ont tout le weekend pour soumettre leurs demandes
- Attribution juste selon la waiver priority

---

## 📂 Structure du Code

```
backend/app/worker/
├── __init__.py                      # Package worker
├── main.py                          # Point d'entrée (asyncio loop)
├── scheduler.py                     # Configuration APScheduler
└── tasks/
    ├── __init__.py                  # Exports des tâches
    ├── detect_trades.py             # 06h - Détection des trades
    ├── sync_players.py              # 07h - Sync joueurs
    ├── fetch_boxscores.py           # 08h - Stats des matchs
    ├── calculate_team_scores.py     # 09h - Scores d'équipes
    ├── update_salaries.py           # 10h lun - Salaires dynamiques
    ├── process_waivers.py           # 13h lun - Waiver wire
    └── update_leaderboards.py       # 13h30 - Classements
```

---

## 🚀 Lancement du Worker

### En développement local

```bash
# Depuis le dossier backend/
python -m app.worker.main
```

### Avec Docker (production)

```bash
docker-compose up worker
```

---

## 🔧 Configuration

Le scheduler est configuré dans `scheduler.py` :

```python
scheduler = AsyncIOScheduler(
    timezone="Europe/Paris",
    job_defaults={
        'coalesce': True,        # Groupe les exécutions manquées
        'max_instances': 1,      # Une seule instance par tâche
    }
)
```

### Gestion des erreurs

- **misfire_grace_time** : 1h pour les tâches quotidiennes, 2h pour les lundis
- Si le worker redémarre, il rattrape les tâches manquées dans la fenêtre grace
- Les erreurs sont loggées dans `worker.log` et la console

---

## 📊 Détails des Tâches

### 1️⃣ `detect_nba_trades` (06h)

**API utilisée :** balldontlie.io  
**Base de données :** Player

**Logique :**
1. Récupère tous les joueurs depuis balldontlie.io (pagination)
2. Compare le champ `team` avec la base de données
3. Si changement → update Player.team + log le trade
4. *(Future)* Crée une entrée dans PlayerTeamHistory

**Output :** `🔄 TRADE DÉTECTÉ ! Luka Doncic : DAL → LAL`

---

### 2️⃣ `sync_nba_players` (07h)

**API utilisée :** balldontlie.io  
**Base de données :** Player

**Logique :**
1. Récupère la liste complète des joueurs NBA (600+ joueurs)
2. Upsert : insert si nouveau, update si existant
3. Active/désactive selon le statut API
4. Mapping des positions (G→SG, F→SF, etc.)

**Utilité :** Ajoute les rookies, gère les blessés de longue durée

---

### 3️⃣ `fetch_yesterday_boxscores` (08h)

**API utilisée :** nba_api (stats.nba.com)  
**Base de données :** PlayerGameScore

**Logique :**
1. Récupère la liste des matchs de hier via `scoreboardv2`
2. Pour chaque match, récupère les stats via `boxscoretraditionalv2`
3. Calcule le score fantasy selon le barème officiel (voir formule ci-dessous)
4. Insert dans PlayerGameScore

**Rate limiting :** 0.5s entre chaque requête pour respecter stats.nba.com

**Formule de scoring :**
```python
score = PTS*1.0 + REB*1.2 + AST*1.5 + STL*3.0 + BLK*3.0 - TO*1.5 - PF*0.5
+ Bonus FG% ≥60% (+3)
+ Bonus 3PT ≥3 (+2)
+ Double-Double (+5)
+ Triple-Double (+12)
+ 30+ points (+3)
- 5+ TO (-2)
```

---

### 4️⃣ `calculate_yesterday_team_scores` (09h)

**API utilisée :** Aucune  
**Base de données :** FantasyTeam, FantasyTeamPlayer, PlayerGameScore, FantasyTeamScore

**Logique :**
1. Pour chaque FantasyTeam, récupère les 6 joueurs du roster
2. Somme leurs scores fantasy de la veille
3. Si un joueur n'a pas joué (DNP) → score = 0
4. Insert dans FantasyTeamScore

**Output :** `✅ Lakers Killers : 245.3 pts`

---

### 5️⃣ `update_all_player_salaries` (10h lundi)

**API utilisée :** Aucune  
**Base de données :** Player, PlayerGameScore

**Logique :**
1. Pour chaque joueur actif, récupère les 15 derniers scores
2. Calcule moyenne + écart-type
3. Compte les matchs joués dans les 20 derniers jours
4. Applique la formule dynamique :

```python
base_salary = (avg_fantasy_score / 5) * 1M$
consistency_bonus = base_salary * (1 - std_dev/avg) * 0.15
availability_factor = games_played / 20
final_salary = (base_salary + consistency_bonus) * availability_factor

# Plafonds : 2M$ ≤ salary ≤ 18M$
```

**Résultat :** Les joueurs réguliers et performants deviennent plus chers

---

### 6️⃣ `process_waiver_claims` (13h lundi)

**API utilisée :** Aucune  
**Base de données :** Transfer, FantasyTeam, FantasyTeamPlayer, Player, League

**Logique :**
1. Pour chaque ligue privée, récupère les demandes PENDING
2. Trie par waiver_priority (ordre inverse du classement)
3. Pour chaque demande :
   - Vérifie si le joueur IN est disponible (joueurs uniques)
   - Vérifie le salary cap (≤ 60M$)
   - Si OK → exécute le transfert (drop + add)
   - Met l'équipe en fin de priorité (pénalité)
4. Marque le Transfer comme COMPLETED ou REJECTED

**Output :** `✅ ACCORDÉ : Lakers Killers recrute Luka Doncic`

---

### 7️⃣ `update_leaderboards` (13h30)

**API utilisée :** Aucune  
**Base de données :** League, FantasyTeam, FantasyTeamScore

**Logique :**
1. Pour chaque ligue active :
   - **SOLO** : Cumul des 7 derniers jours (rolling week)
   - **PRIVATE** : Cumul depuis la création (season_start)
2. Calcule le score total de chaque équipe
3. Trie par score décroissant
4. Affiche le classement avec médailles 🥇🥈🥉

**Future :** Sauvegarder dans une table `LeagueLeaderboard` ou cache Redis

---

## 📝 Logs

Le worker génère des logs détaillés :

```
2025-11-XX 08:05:12 | INFO | ================================================================================
2025-11-XX 08:05:12 | INFO | 📊 RÉCUPÉRATION DES BOXSCORES NBA - DÉBUT
2025-11-XX 08:05:12 | INFO | ================================================================================
2025-11-XX 08:05:12 | INFO | 📅 Date cible : 2025-11-03
2025-11-XX 08:05:13 | INFO | ✅ 8 match(s) trouvé(s)
2025-11-XX 08:05:15 | INFO |    ⭐ Giannis Antetokounmpo : 67.9 pts fantasy !
```

**Emplacement :** `worker.log` (dans le dossier backend/)

---

## 🐳 Docker Configuration

Dans `docker-compose.yml`, le worker est un service séparé :

```yaml
worker:
  build:
    context: ./backend
    dockerfile: Dockerfile.worker
  depends_on:
    - db
  environment:
    DATABASE_URL: postgresql://user:pass@db:5432/nba_fantasy
  restart: always
```

**Dockerfile.worker** (à créer) :
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "app.worker.main"]
```

---

## ⚠️ Points d'Attention

### Rate Limiting
- **balldontlie.io** : Pas de limite (API gratuite)
- **nba_api / stats.nba.com** : ~0.5s entre chaque requête recommandé

### Gestion des erreurs
- Chaque tâche a son propre try/except
- Les erreurs n'arrêtent pas le scheduler
- Logs détaillés pour debug

### Performance
- Commit par batch (tous les 5 matchs, 20 équipes, 100 joueurs)
- Évite les timeouts PostgreSQL
- Rollback en cas d'erreur

---

## 🔮 Améliorations Futures

1. **Cache Redis** pour les leaderboards
2. **Webhooks** pour notifier les utilisateurs (trade, waiver)
3. **Monitoring** avec Prometheus + Grafana
4. **Table PlayerTeamHistory** pour l'historique complet des trades
5. **Alertes** Slack/Discord en cas d'erreur critique
6. **Retry logic** avec exponentiel backoff pour les API

---

## 📞 Contact

Pour toute question sur le worker :
- Logs : `backend/worker.log`
- Code : `backend/app/worker/`
- Tests : Exécuter manuellement une tâche avec `python -m app.worker.tasks.detect_trades`

---

**Dernière mise à jour :** Novembre 2025  
**Auteur :** Projet NBA Fantasy League "Starting Six"
