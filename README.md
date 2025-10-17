# NBA Fantasy League "Starting Six" 🏀

Application web de fantasy basketball avec gestion d'équipes, système de salaire et classement quotidien basé sur les performances réelles des joueurs NBA.

## 📋 Fonctionnalités

- Création d'équipes de 6 joueurs (PG, SG, SF, PF, C, + 1 UTIL)
- Système de salary cap (budget limité)
- Mise à jour quotidienne des scores basés sur les stats réelles NBA
- Classement global des utilisateurs
- Authentification JWT

## 🛠️ Stack Technique

- **Backend**: FastAPI + Python
- **Base de données**: PostgreSQL
- **ORM**: SQLAlchemy
- **Conteneurisation**: Docker & Docker Compose
- **API externe**: balldontlie.io
- **Tests**: Pytest

## 🏗️ Architecture

Le projet est composé de 3 services principaux:

1. **API** - Gestion des utilisateurs, équipes et endpoints REST
2. **Database** - PostgreSQL pour la persistance des données
3. **Worker** - Service de mise à jour automatique (joueurs NBA, calculs de scores)

## 🚀 Démarrage rapide

```bash
# Cloner le projet
git clone https://github.com/ton-username/nba-fantasy-league.git
cd nba-fantasy-league

# Copier le fichier d'environnement
cp .env.example .env

# Lancer les services avec Docker
docker-compose up -d

# L'API sera disponible sur http://localhost:8000
```

## 📚 Documentation

La documentation de l'API est disponible sur:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Tests

```bash
# Exécuter les tests
docker-compose exec api pytest

# Avec couverture
docker-compose exec api pytest --cov=app
```

## 📈 Système de scoring

- Points: +1
- Rebonds: +1.2
- Passes décisives: +1.5
- Interceptions/Contres: +3
- Balles perdues: -2
- Double-double: +5
- Triple-double: +10

## 📝 Licence

MIT
