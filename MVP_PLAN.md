# 🎯 PLAN MVP - NBA Fantasy "Starting Six"

## ✅ DÉJÀ FAIT (80%)

### Backend (100%)
- ✅ Architecture FastAPI complète
- ✅ Modèles SQLAlchemy (User, Player, FantasyTeam, League, Scores, Transfers)
- ✅ Base PostgreSQL fonctionnelle
- ✅ API NBA synchronisée (495 joueurs actifs 2025-26)
- ✅ Position mapping intelligent (PG: 47, SG: 160, SF: 167, PF: 49, C: 72)
- ✅ Authentification JWT
- ✅ Endpoints CRUD complets
- ✅ Worker prêt (calcul scores, salaires)

### Frontend (70%)
- ✅ Next.js 16 + TypeScript
- ✅ Pages : Login, Register, Dashboard, Team, Players, Leaderboard
- ✅ AuthContext fonctionnel
- ✅ Components shadcn/ui
- ✅ Layouts responsive
- ✅ Formulaires validés

---

## 🔧 À FINALISER POUR MVP (20%)

### 1. **Création d'équipe complète** (PRIORITÉ 1) 🔴
**Objectif :** Permettre à l'utilisateur de créer son équipe Starting Six

**Actions :**
- [ ] Tester création équipe Solo League (endpoint `/teams/create`)
- [ ] Vérifier modal ajout joueur (AddPlayerModal)
- [ ] Tester ajout 6 joueurs (PG, SG, SF, PF, C, UTIL)
- [ ] Valider salary cap (60M$)
- [ ] Afficher roster complet dans `/team`

**Tests à faire :**
```bash
# Test création équipe
POST /api/v1/teams/create
{
  "name": "Mon équipe test",
  "league_type": "SOLO"
}

# Test ajout joueur
POST /api/v1/roster/{team_id}/add-player
{
  "player_id": 201939,  # Stephen Curry
  "roster_slot": "PG"
}
```

**Fichiers concernés :**
- `frontend/src/app/team/page.tsx`
- `frontend/src/components/AddPlayerModal.tsx`
- `backend/app/api/v1/endpoints/roster.py`

---

### 2. **Worker - Calcul des scores** (PRIORITÉ 2) 🟡
**Objectif :** Calculer automatiquement les scores fantasy journaliers

**Actions :**
- [ ] Tester `fetch_and_save_boxscores(date)` manuellement
- [ ] Vérifier calcul fantasy_score (PTS, REB, AST, STL, BLK, TO)
- [ ] Tester `calculate_team_scores(date)` 
- [ ] Afficher scores dans Dashboard

**Test manuel :**
```python
cd backend
python -c "from app.worker.tasks.scores import fetch_and_save_boxscores; from datetime import date; fetch_and_save_boxscores(date(2024, 11, 20))"
```

**Fichiers concernés :**
- `backend/app/worker/tasks/scores.py`
- `frontend/src/app/dashboard/page.tsx`

---

### 3. **Dashboard avec stats** (PRIORITÉ 3) 🟢
**Objectif :** Afficher les infos importantes de l'équipe

**Afficher :**
- [ ] Score total de l'équipe (dernière journée)
- [ ] Rang dans Solo League
- [ ] Budget utilisé / 60M$
- [ ] Historique des 5 derniers scores

**Mockup Dashboard :**
```
┌─────────────────────────────────────┐
│ 🏆 Mon Équipe - Rang #42/1,234      │
├─────────────────────────────────────┤
│ Score hier : 245.5 pts              │
│ Budget : 30M$ / 60M$ (50%)          │
│                                      │
│ Historique :                         │
│ 02/12: 245.5 pts                     │
│ 01/12: 198.3 pts                     │
│ 30/11: 267.1 pts                     │
└─────────────────────────────────────┘
```

**Fichier :** `frontend/src/app/dashboard/page.tsx`

---

### 4. **Leaderboard Solo League** (PRIORITÉ 4) 🟢
**Objectif :** Classement global des équipes

**Afficher :**
- [ ] Top 100 équipes
- [ ] Score total cumulé
- [ ] Nom d'équipe + propriétaire
- [ ] Pagination

**Endpoint :** `GET /api/v1/leagues/solo/leaderboard`

**Fichier :** `frontend/src/app/leaderboard/page.tsx`

---

### 5. **Transferts de base** (PRIORITÉ 5) 🟢
**Objectif :** Retirer/Ajouter un joueur

**Actions :**
- [ ] Bouton "Retirer" sur chaque joueur
- [ ] Modal "Remplacer par..." (même poste)
- [ ] Vérifier salary cap après transfert
- [ ] Limite 2 transferts/semaine

**Endpoint :** 
```
DELETE /api/v1/roster/{team_id}/remove-player/{player_id}
POST /api/v1/roster/{team_id}/add-player
```

---

## 🚀 PLAN D'EXÉCUTION (4 heures)

### Phase 1 : Test création équipe (1h)
1. Relancer services (`.\start_project.ps1`)
2. Créer compte test
3. Créer équipe "Test MVP"
4. Ajouter 6 joueurs (1 de chaque poste)
5. Vérifier affichage roster complet
6. **BLOCKER si ça marche pas → fixer avant de continuer**

### Phase 2 : Worker scores (1h30)
1. Récupérer boxscores pour une date passée (ex: 20 Nov 2024)
2. Vérifier insertion dans `player_game_scores`
3. Calculer scores d'équipes
4. Vérifier insertion dans `fantasy_team_scores`

### Phase 3 : Dashboard + Leaderboard (1h)
1. Afficher score équipe sur Dashboard
2. Afficher rang Solo League
3. Implémenter leaderboard basique
4. Tester pagination

### Phase 4 : Polish + Tests (30min)
1. Tester transferts
2. Messages d'erreur clairs
3. Loading states
4. Validation formulaires

---

## ✅ CRITÈRES DE SUCCÈS MVP

**L'utilisateur peut :**
1. ✅ Créer un compte
2. ✅ Se connecter
3. ⚠️ Créer une équipe de 6 joueurs (À TESTER)
4. ❌ Voir le score de son équipe (Pas encore implémenté)
5. ❌ Voir son classement (Pas encore implémenté)
6. ⚠️ Faire des transferts (À TESTER)

**Statut actuel : 2/6 validés ✅, 2/6 à tester ⚠️, 2/6 à implémenter ❌**

---

## 🎯 APRÈS MVP (Nice-to-have)

- 📊 Page statistiques détaillées
- 📱 Mobile responsive optimisé
- 🔔 Notifications transferts
- 📈 Graphiques de performance
- 🏆 Private Leagues
- 💬 Chat entre joueurs
- 📧 Email notifications

---

## 🔥 COMMENCER MAINTENANT

**Prochaine action :** Tester création d'équipe complète
```bash
# 1. S'assurer que les services tournent
.\start_project.ps1

# 2. Ouvrir navigateur
http://localhost:3000/team

# 3. Créer équipe et ajouter 6 joueurs
```

**Si ça fonctionne → Passer au Worker**  
**Si ça bloque → Fixer avant de continuer**
