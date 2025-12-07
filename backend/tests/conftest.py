"""Configuration et fixtures partagées pour les tests pytest"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.utilisateur import Utilisateur
from app.models.player import Player
from app.core.auth import hash_password

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée une nouvelle session de base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Client de test FastAPI avec base de données isolée"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Crée un utilisateur de test"""
    user = Utilisateur(
        nom_utilisateur="testuser",
        mot_de_passe_hash=hash_password("testpass123"),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Crée un administrateur de test"""
    admin = Utilisateur(
        nom_utilisateur="admin",
        mot_de_passe_hash=hash_password("admin123"),
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """Headers d'authentification pour les requêtes"""
    response = client.post(
        "/api/v1/auth/connexion",
        json={
            "nom_utilisateur": "testuser",
            "mot_de_passe": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    """Headers d'authentification admin"""
    response = client.post(
        "/api/v1/auth/connexion",
        json={
            "nom_utilisateur": "admin",
            "mot_de_passe": "admin123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_players(db_session):
    """Crée des joueurs NBA de test"""
    from app.models.player import Position
    players = [
        Player(
            external_api_id=2544,
            full_name="LeBron James",
            first_name="LeBron",
            last_name="James",
            position=Position.SF,
            team="Los Angeles Lakers",
            team_abbreviation="LAL",
            fantasy_cost=16000000.0,
            is_active=True
        ),
        Player(
            external_api_id=201939,
            full_name="Stephen Curry",
            first_name="Stephen",
            last_name="Curry",
            position=Position.PG,
            team="Golden State Warriors",
            team_abbreviation="GSW",
            fantasy_cost=15500000.0,
            is_active=True
        ),
        Player(
            external_api_id=203507,
            full_name="Giannis Antetokounmpo",
            first_name="Giannis",
            last_name="Antetokounmpo",
            position=Position.PF,
            team="Milwaukee Bucks",
            team_abbreviation="MIL",
            fantasy_cost=17000000.0,
            is_active=True
        ),
    ]
    for player in players:
        db_session.add(player)
    db_session.commit()
    return players
