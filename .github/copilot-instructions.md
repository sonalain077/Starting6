Projet Fullstack Data : NBA Fantasy League "Starting Six"
Ce projet est une application web fullstack permettant de gérer une ligue de fantasy basketball basée sur les performances réelles des joueurs de la NBA. Le concept unique de "Starting Six" impose aux utilisateurs de construire une équipe de 6 joueurs respectant les postes traditionnels du basketball et un plafond salarial (salary cap).

🚀 Concept du Projet
L'application permet à un utilisateur de s'inscrire, de créer son équipe de rêve en choisissant 6 joueurs de la NBA, et de compétitionner contre d'autres utilisateurs. Le score de chaque équipe est calculé quotidiennement en fonction des statistiques réelles des joueurs lors des matchs de la veille. Un leaderboard général permet de suivre le classement en temps réel.

Contraintes Stratégiques
Formation de l'équipe : 1 Meneur (PG), 1 Arrière (SG), 1 Ailier (SF), 1 Ailier Fort (PF), 1 Pivot (C) et 1 Sixième Homme (UTIL - n'importe quelle position).

Plafond Salarial (Salary Cap) : Chaque utilisateur dispose d'un budget fixe (ex: 100M$) pour composer son équipe. La valeur de chaque joueur est calculée dynamiquement en fonction de ses performances.

🛠️ Stack Technique
Backend : Python avec le framework FastAPI.

Base de Données : PostgreSQL, gérée avec l'ORM SQLAlchemy.

Conteneurisation : Docker & Docker Compose pour orchestrer les services de l'application.

Authentification : Gestion par tokens JWT (JSON Web Tokens) pour sécuriser les routes de l'API.

Tests : Suite de tests automatisés avec Pytest.

API Externe : balldontlie.io pour la récupération des données des joueurs, des matchs et des statistiques de la NBA.

🏛️ Architecture
L'application est conçue autour d'une architecture à trois services, orchestrée par Docker Compose :

API Backend (api)

C'est le point d'entrée pour le client (navigateur web ou application mobile).

Gère l'inscription, l'authentification des utilisateurs, la création et la modification des équipes.

Expose les endpoints pour consulter la liste des joueurs, son équipe, et le leaderboard.

L'API ne fait aucun calcul lourd. Elle se contente de lire et d'écrire dans la base de données.

Base de Données (db)

Un service PostgreSQL qui stocke toutes les données persistantes de l'application : utilisateurs, joueurs, équipes, scores, etc.

Sert de source de vérité unique pour l'API et le Worker.

Worker (worker)

C'est le moteur "data" du projet. C'est un script Python qui s'exécute en arrière-plan.

Responsabilités :

Peupler la BDD : Une fois au lancement, il récupère la liste de tous les joueurs de la NBA et leurs informations via l'API externe.

Calculer la valeur des joueurs : Il exécute une formule pour déterminer le fantasy_cost de chaque joueur en fonction de ses performances passées.

Mettre à jour les scores quotidiennement : Chaque nuit, il se réveille, interroge l'API externe pour les stats des matchs de la veille, calcule le score fantasy de chaque joueur, et met à jour le score total de chaque équipe dans la base de données.

📊 Modèle de Données (SQLAlchemy)
La base de données est structurée autour des modèles suivants :

User: Stocke les informations des utilisateurs (username, email, mot de passe hashé).

Player: Contient la liste de tous les joueurs réels de la NBA.

id, external_api_id, full_name, position ('PG', 'SG'...), fantasy_cost.

FantasyTeam: Représente l'équipe créée par un utilisateur.

id, name, user_id (lien vers User).

Possède une relation plusieurs-à-plusieurs avec la table Player.

PlayerGameScore: Enregistre le score fantasy d'un joueur pour un match spécifique.

id, player_id, game_date, fantasy_score.

FantasyTeamScore: Agrége le score total d'une équipe pour une journée.

id, team_id, score_date, total_score.

🧠 Logique Métier Clé
Calcul du Score Fantasy d'un Joueur
Le score est calculé par le Worker à partir des statistiques d'un match réel en utilisant le barème suivant :

Point : +1

Rebond : +1.2

Passe décisive : +1.5

Interception / Contre : +3

Balle perdue : -2

Bonus Double-Double : +5

Bonus Triple-Double : +10

Règles de Gestion de l'Équipe
Toute la logique de validation (respect du budget, des postes, et du nombre de joueurs) est gérée par l'API au moment où un utilisateur tente d'ajouter un joueur à son équipe.

⚙️ Installation et Lancement du Projet
Clonez le dépôt GitHub.

Assurez-vous que Docker et Docker Compose sont installés sur votre machine.

À la racine du projet, exécutez la commande suivante pour construire et démarrer les conteneurs :

Bash

docker-compose up --build
L'API sera accessible à l'adresse http://localhost:8000.

Script de Remplissage
Le projet inclut un script (exécuté par le service worker au premier lancement) qui remplit la base de données avec la liste des joueurs de la NBA, leur position, et leur coût initial, afin que l'application soit immédiatement utilisable.