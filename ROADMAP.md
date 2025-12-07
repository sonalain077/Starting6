# 🗺️ ROADMAP - NBA Fantasy League "Starting Six"

**Projet :** Application fullstack de fantasy basketball  
**Status actuel :** ✅ Système backend fonctionnel avec données réelles NBA  
**Date :** 5 novembre 2025

---

# 🎯 ROADMAP ESSENTIELLE (MVP FONCTIONNEL)

## ✅ PHASE 1 : BACKEND (TERMINÉE)

### Backend Core ✅
- [x] Configuration PostgreSQL + SQLAlchemy
- [x] Modèles de données (12 tables)
- [x] Authentification JWT
- [x] API REST avec FastAPI
- [x] Endpoints CRUD de base

### Intégration NBA API ✅
- [x] Connexion live.nba API (temps réel)
- [x] Récupération boxscores quotidiens
- [x] Parsing données NBA → fantasy scores
- [x] Système de fallback (live.nba → stats.endpoints)

### Système Worker ✅
- [x] Worker fetch_boxscores (140 scores/jour)
- [x] Worker calculate_team_scores
- [x] Worker update_leaderboards
- [x] Worker update_salaries
- [x] Scheduler APScheduler

### Moteur de Scoring ✅
- [x] Calcul fantasy score (barème complet)
- [x] Bonus d'efficacité (FG%, 3PT, FT%)
- [x] Bonus de performance (double-double, triple-double)
- [x] Pénalités (TO, fautes, DQ)
- [x] Salaire dynamique basé sur performances

### Tests & Validation ✅
- [x] Pipeline test end-to-end (5 étapes)
- [x] Rosters complets (6/6 joueurs)
- [x] Scores calculés correctement
- [x] Leaderboard fonctionnel

---

## 🚀 PHASE 2 : FRONTEND ESSENTIEL (À FAIRE)

**Objectif :** Interface utilisateur fonctionnelle pour jouer  
**Durée estimée :** 3-4 semaines

### Week 1 : Setup & Authentification
- [ ] **Init Next.js 15** avec App Router + TypeScript
- [ ] **Tailwind CSS + shadcn/ui** pour le design
- [ ] **Page Login/Register** (formulaires basiques)
- [ ] **Gestion JWT tokens** (localStorage)
- [ ] **Protected routes** (middleware)
- [ ] **API client** (fetch wrapper avec types)

### Week 2 : Mon Équipe & Dashboard
- [ ] **Layout principal** (header, nav, footer)
- [ ] **Page Dashboard** (vue d'ensemble)
  - Score total de mon équipe
  - Mon rang dans le classement
  - Budget utilisé / restant
- [ ] **Page Mon Équipe** (roster 6/6)
  - Affichage des 6 joueurs (PG, SG, SF, PF, C, UTIL)
  - Nom, position, équipe NBA, coût
  - Score fantasy de chaque joueur

### Week 3 : Transferts & Joueurs
- [ ] **Page Liste Joueurs NBA** (tous les ~600 joueurs)
  - Tableau avec tri et filtres basiques
  - Filtrer par position
  - Recherche par nom
  - Voir coût et score moyen
- [ ] **Système de Transfert**
  - Cliquer sur joueur pour remplacer
  - Validation contraintes (position, budget)
  - Confirmation avant transfert
  - Message succès/erreur

### Week 4 : Leaderboard & Finitions
- [ ] **Page Leaderboard SOLO League**
  - Classement de toutes les équipes
  - Score total + rang
  - Voir équipe adverse (composition)
- [ ] **Page Statistiques Simples**
  - Top 10 joueurs de la semaine
  - Historique de mes scores (liste)
- [ ] **Responsive mobile basique**
- [ ] **Tests manuels complets**

---

## 🚀 PHASE 3 : DÉPLOIEMENT PRODUCTION (À FAIRE)

**Objectif :** Mettre l'app en ligne  
**Durée estimée :** 1 semaine

### Hébergement Simple
- [ ] **Frontend** → Vercel (gratuit, auto-deploy)
- [ ] **Backend** → Railway ou Render (gratuit tier)
- [ ] **Database** → Supabase ou Neon (PostgreSQL gratuit)

### Configuration Minimale
- [ ] Variables d'environnement production
- [ ] CORS configuré pour frontend
- [ ] Worker qui tourne quotidiennement (cron)
- [ ] Logs basiques (print statements)

---

## ✅ CE QUI EST PRÊT À DEPLOYER

- ✅ Backend API complet
- ✅ Worker quotidien (scores NBA)
- ✅ Base de données structurée
- ✅ Système de scoring fonctionnel
- ✅ Leaderboard automatique

---

## ❌ CE QUI N'EST PAS NÉCESSAIRE (OPTIONNEL)

### ❌ Performance Avancée
- Redis cache
- Pagination complexe
- Optimisation hardcore

### ❌ Features Avancées
- Draft en temps réel
- Weekly matchups
- Système playoff
- Achievements/badges
- IA prédictions

### ❌ Mobile Natif
- App React Native
- Notifications push natives
- Widgets

### ❌ Sécurité Entreprise
- Audit complet
- RGPD compliance
- Terms of Service

### ❌ Marketing/Monétisation
- Landing page
- SEO
- Analytics
- Premium features
- Revenue streams

---

## � CE QU'IL RESTE VRAIMENT À FAIRE

### ✅ Backend → TERMINÉ
- API REST fonctionnelle
- Worker quotidien
- Scoring automatique

### 🔄 Frontend → 4 SEMAINES
1. **Week 1 :** Setup + Auth
2. **Week 2 :** Dashboard + Mon Équipe
3. **Week 3 :** Transferts + Liste Joueurs
4. **Week 4 :** Leaderboard + Polish

### 🚀 Déploiement → 1 SEMAINE
- Vercel + Railway + Supabase
- Tout gratuit pour commencer

---

## 🎯 TOTAL : 5 SEMAINES POUR APP FONCTIONNELLE

**Après ces 5 semaines, tu auras :**
✅ Une app web complète et jouable  
✅ Authentification fonctionnelle  
✅ Gestion de ton équipe (6 joueurs)  
✅ Faire des transferts  
✅ Voir le classement  
✅ Scores mis à jour automatiquement chaque jour  
✅ Déployée en ligne (accessible par URL)  

**Tu pourras :**
✅ Créer un compte  
✅ Construire ton équipe  
✅ Faire des transferts  
✅ Suivre tes performances  
✅ Comparer avec les autres  
✅ Jouer toute la saison NBA !  

---

## 🔥 ACTION IMMÉDIATE (CETTE SEMAINE)

### Jour 1-2 : Setup
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npx shadcn-ui@latest init
```

### Jour 3-4 : Auth
- Login/Register pages
- JWT storage
- Protected routes

### Jour 5-7 : Premier écran
- Dashboard basique
- Afficher mon équipe
- Connection à l'API

---

## � CHECKLIST FINALE MVP

### Backend ✅
- [x] API REST complète
- [x] Worker quotidien NBA
- [x] Système de scoring
- [x] Base de données
- [x] Authentification JWT

### Frontend 🔄 (4 semaines)
- [ ] Setup Next.js + Auth
- [ ] Dashboard + Mon Équipe
- [ ] Transferts + Joueurs
- [ ] Leaderboard + Polish

### Déploiement 🚀 (1 semaine)
- [ ] Deploy frontend (Vercel)
- [ ] Deploy backend (Railway)
- [ ] Deploy DB (Supabase)
- [ ] Tester en production

### Total : 5 SEMAINES = APP FONCTIONNELLE ✅

---

**Dernière mise à jour :** 5 novembre 2025  
**Version :** 2.0 - MVP Essentiel  
**Status :** ✅ Backend prêt | 🔄 Frontend 4 semaines | 🚀 Deploy 1 semaine
