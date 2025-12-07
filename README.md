# NBA Fantasy League - Starting Six

## Informations du projet

**Auteur**: Pham Dang Son Alain  
**Formation**: DSIA 5102A - Application Fullstack Data  
**Repository**: [Starting6](https://github.com/sonalain077/Starting6)  
**Année**: 2025-2026

---

## Table des matières

1. [Choix du sujet](#choix-du-sujet)
2. [Architecture du projet](#architecture-du-projet)
3. [Technologies utilisées](#technologies-utilisées)
4. [Fonctionnalités implémentées](#fonctionnalités-implémentées)
5. [Installation et lancement](#installation-et-lancement)
6. [Difficultés rencontrées](#difficultés-rencontrées)
7. [Pistes d'amélioration](#pistes-damélioration)
8. [Conclusion](#conclusion)

---

## Choix du sujet

Étant passionné de basketball depuis plusieurs années, j'ai choisi de développer une application de fantasy league NBA. L'idée était de créer quelque chose qui me motive réellement tout en relevant un défi technique intéressant.

Le concept de **Starting Six** est inspiré des fantasy leagues classiques mais avec une contrainte unique : au lieu de gérer un roster de 12-15 joueurs, l'utilisateur doit composer une équipe de seulement 6 joueurs en respectant les postes du basketball (PG, SG, SF, PF, C + 1 UTIL) et un plafond salarial de 60 millions de dollars.

Ce qui m'a particulièrement intéressé dans ce projet :
- Travailler avec des données réelles (statistiques NBA)
- Implémenter un système de scoring complexe basé sur les performances réelles des joueurs
- Créer un système de salaires dynamiques qui évolue selon les performances
- Gérer la synchronisation quotidienne des données via un worker automatisé

---

## Architecture du projet

Le projet suit une architecture microservices conteneurisée avec Docker Compose :

```
ProjetFullstack/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuration, auth, database
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── schemas/        # Schémas Pydantic
│   │   └── worker/         # Scripts de synchronisation
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # Application Next.js
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # Composants React
│   │   ├── context/       # Auth context
│   │   └── lib/           # Utilitaires et API client
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml      # Orchestration des services
└── README.md
```

### Services Docker

Le projet utilise 4 conteneurs :

1. **db** (PostgreSQL 15) : Base de données relationnelle
2. **api** (FastAPI) : Backend REST avec Python
3. **frontend** (Next.js 16) : Interface utilisateur
4. **worker** : Script Python qui tourne en arrière-plan pour synchroniser les données NBA

---

## Technologies utilisées

### Backend
- **FastAPI** : Framework web moderne et rapide pour Python
- **SQLAlchemy** : ORM pour gérer la base de données
- **PostgreSQL** : Base de données relationnelle
- **JWT** : Authentification par tokens
- **bcrypt** : Hashage sécurisé des mots de passe
- **APScheduler** : Planification des tâches automatiques
- **nba_api** : Bibliothèque pour récupérer les statistiques NBA

### Frontend
- **Next.js 16** : Framework React avec App Router
- **TypeScript** : Typage statique pour JavaScript
- **Tailwind CSS** : Framework CSS utilitaire
- **shadcn/ui** : Bibliothèque de composants UI

### DevOps
- **Docker** : Conteneurisation de l'application
- **Docker Compose** : Orchestration multi-conteneurs

---

## Fonctionnalités implémentées

### Gestion des utilisateurs et authentification

- Inscription avec validation des données (username unique, mot de passe hashé)
- Connexion avec génération de token JWT
- Middleware d'authentification pour sécuriser les endpoints
- Système d'administration (promotion/rétrogradation d'utilisateurs)
- Gestion des sessions côté client avec Context API

### Système de fantasy league

**Création d'équipe** :
- Sélection de 6 joueurs NBA respectant les contraintes de postes
- Respect du salary cap de 60M$ (salaires dynamiques)
- Validation des contraintes en temps réel

**Calcul de score quotidien** :
- Récupération automatique des boxscores NBA via l'API publique
- Système de points complexe basé sur 15+ statistiques
- Bonus pour performances exceptionnelles (double-double, triple-double, efficacité)
- Pénalités pour mauvaises performances

**Classement et leaderboards** :
- Classement SOLO global (tous les utilisateurs)
- Support pour ligues privées (à venir)

### Worker automatisé

Un script Python tourne en permanence pour :
- Synchroniser la liste des joueurs NBA
- Récupérer les statistiques de matchs quotidiennement
- Calculer les scores fantasy de chaque équipe
- Mettre à jour les salaires des joueurs chaque semaine
- Traiter les transferts dans les ligues privées

### Gestion des erreurs HTTP

Toutes les routes API implémentent une gestion d'erreurs complète :
- 400 Bad Request : Données invalides
- 401 Unauthorized : Non authentifié
- 403 Forbidden : Permissions insuffisantes
- 404 Not Found : Ressource inexistante
- 500 Internal Server Error : Erreurs serveur

Les erreurs sont propagées au frontend avec des messages explicites.

---

## Installation et lancement

### Prérequis

- Docker Desktop installé et lancé
- Git
- PowerShell (Windows) ou Bash (Linux/Mac)

### Étapes d'installation

1. **Cloner le repository** :
```bash
git clone https://github.com/sonalain077/Starting6.git
cd Starting6
```

2. **Configurer les variables d'environnement** :

Créer un fichier `.env` à la racine :
```env
POSTGRES_DB=nba_fantasy
POSTGRES_USER=fantasy_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise
SECRET_KEY=votre_cle_secrete_jwt
```

3. **Lancer l'application avec Docker Compose** :
```bash
docker-compose up -d --build
```

4. **Vérifier que tous les services sont actifs** :
```bash
docker-compose ps
```

Vous devriez voir 4 conteneurs en état "Up".

5. **Accéder à l'application** :

Au lancement du frontend se déconnecté d'abord pour créer un compte : 

- Frontend : http://localhost:3000
- API Documentation : http://localhost:8000/docs
- Base de données : localhost:5432

### Initialisation de la base de données

Au premier lancement, la base de données est automatiquement initialisée avec (Attention prend un peu de temps du au lancement du scraping des joueurs) :
- Création des tables (users, players, teams, scores, etc.)
- Import initial des joueurs NBA actifs

Pour créer un compte administrateur :
```bash
docker-compose exec api python create_admin.py
```

---

## Difficultés rencontrées

### 1. Gestion des APIs externes

**Problème** : Les APIs NBA gratuites sont limitées et parfois instables.

**Solutions testées** :
- Première tentative avec balldontlie.io : API simple mais manque de statistiques détaillées
- Migration vers nba_api : Plus complet mais documentation parfois floue
- Implémentation d'un système de cache pour limiter les appels
- Gestion des rate limits avec des délais entre requêtes


### 2. Calcul du système de scoring

**Problème** : Créer un barème équilibré qui valorise toutes les contributions d'un joueur.

**Difficultés** :
- Pondérer correctement chaque statistique (points, rebonds, passes, etc.)
- Éviter qu'un seul type de joueur (scoreurs) domine
- Gérer les cas particuliers (triple-double, match parfait)

**Solution finale** : Après plusieurs itérations et tests avec des matchs réels, j'ai créé un système à trois niveaux :
- Points de base par statistique
- Bonus d'efficacité (FG%, AST/TO ratio)
- Bonus de performance globale (double-double, etc.)

### 3. Architecture Docker et réseau

**Problème** : Confusion entre localhost dans les conteneurs vs l'hôte.

**Erreur classique** :
```yaml
NEXT_PUBLIC_API_URL=http://api:8000  # Ne marche pas depuis le navigateur!
```

**Explication** : Les appels fetch de Next.js sont exécutés dans le navigateur (côté client), pas dans le conteneur Docker. Le navigateur ne connaît pas le nom de service Docker "api", il faut utiliser localhost.

**Solution** :
```yaml
NEXT_PUBLIC_API_URL=http://localhost:8000  # Fonctionne depuis le navigateur
```

## Pistes d'amélioration

En réfléchissant à l'évolution du projet, plusieurs axes d'amélioration me semblent prioritaires. Au début du développement, j'avais imaginé un système complet de ligues privées qui permettrait à un groupe d'amis de créer leur propre compétition fermée avec des règles spécifiques. L'idée était d'implémenter un mécanisme de draft en début de saison où chaque joueur NBA ne pourrait appartenir qu'à une seule équipe, créant ainsi une vraie compétition stratégique. J'avais également pensé à un système de waiver wire avec priorité inversée au classement, permettant chaque lundi de recruter les joueurs libres selon un ordre défini. Malheureusement, la complexité de cette fonctionnalité et les contraintes de temps m'ont poussé à me concentrer d'abord sur la version SOLO, plus accessible mais moins stratégique.

Un autre aspect que je trouve passionnant serait d'intégrer des analyses statistiques avancées pour aider les utilisateurs dans leurs choix. Par exemple, développer un système de prédiction des performances basé sur l'historique des joueurs face à certaines équipes, ou selon qu'ils jouent à domicile ou à l'extérieur. On pourrait également créer des graphiques d'évolution des scores fantasy sur les dernières semaines pour identifier les joueurs en forme montante ou descendante. J'avais même pensé à utiliser des algorithmes de machine learning simples pour suggérer automatiquement les meilleurs transferts possibles en fonction du budget disponible et du calendrier NBA à venir. Ces outils d'aide à la décision transformeraient l'application d'un simple jeu de fantasy en un véritable outil d'analyse sportive.

## Conclusion

Ce projet m'a permis de mettre en pratique l'ensemble des concepts du fullstack moderne :

**Côté backend** :
- Architecture REST avec FastAPI
- Gestion de base de données relationnelle complexe
- Authentification et autorisation
- Workers asynchrones pour tâches de fond
- Intégration d'APIs tierces

**Côté frontend** :
- Application React moderne avec Next.js 16
- Gestion d'état avec Context API
- Communication API avec gestion d'erreurs
- Interface utilisateur responsive

**DevOps** :
- Conteneurisation complète avec Docker
- Orchestration multi-services
- Variables d'environnement et configuration

Au-delà des aspects techniques, ce projet m'a surtout appris l'importance de la planification. J'aurais dû passer plus de temps au début à concevoir la structure de données et l'architecture avant de coder. J'ai dû refactoriser plusieurs fois le code, notamment pour le système de salaires dynamiques que je n'avais pas prévu initialement.

La gestion des erreurs et des cas limites est aussi quelque chose que j'ai sous-estimé. Par exemple, que se passe-t-il si un joueur est transféré d'équipe NBA en cours de saison ? Ou s'il se blesse ? Ces cas nécessitent une réflexion approfondie.

Enfin, travailler avec des données réelles ajoute une complexité qu'on ne retrouve pas dans les projets académiques classiques. Les APIs peuvent tomber, les données peuvent être incohérentes, il faut gérer les délais de mise à jour... C'est une expérience très formatrice.

Je suis satisfait du résultat actuel mais conscient qu'un produit complet nécessiterait encore plusieurs mois de développement, notamment sur les aspects tests, monitoring et scalabilité.

---

## Annexes

### Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f api

# Accéder au shell d'un conteneur
docker-compose exec api bash

# Arrêter tous les services
docker-compose down

# Reconstruire après modifications
docker-compose up -d --build

# Réinitialiser complètement (supprime les données!)
docker-compose down -v
docker-compose up -d --build
```

### Structure de la base de données

Tables principales :
- `utilisateurs` : Comptes utilisateurs
- `players` : Joueurs NBA avec salaires fantasy
- `fantasy_teams` : Équipes des utilisateurs
- `fantasy_team_players` : Association équipes-joueurs
- `player_game_scores` : Scores quotidiens des joueurs
- `fantasy_team_scores` : Scores quotidiens des équipes
- `leagues` : Ligues (SOLO et PRIVATE)

### API Endpoints principaux

```
POST   /api/v1/auth/inscription
POST   /api/v1/auth/connexion
GET    /api/v1/players
GET    /api/v1/teams/me
POST   /api/v1/teams
POST   /api/v1/roster/add
GET    /api/v1/leagues/solo/leaderboard
GET    /api/v1/utilisateurs/admin/all
```

Documentation complète : http://localhost:8000/docs

---

**Date de rendu** : Décembre 2024  
**Version** : 1.0.0
