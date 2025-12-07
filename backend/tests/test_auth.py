"""Tests pour l'authentification et la gestion des utilisateurs"""
import pytest


class TestAuthentication:
    """Tests des endpoints d'authentification"""

    def test_inscription_success(self, client):
        """Test d'inscription réussie"""
        response = client.post(
            "/api/v1/auth/inscription",
            json={
                "nom_utilisateur": "newuser",
                "mot_de_passe": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_inscription_duplicate_username(self, client, test_user):
        """Test d'inscription avec nom d'utilisateur existant"""
        response = client.post(
            "/api/v1/auth/inscription",
            json={
                "nom_utilisateur": "testuser",
                "mot_de_passe": "password123"
            }
        )
        assert response.status_code == 400
        assert "déjà" in response.json()["detail"].lower()

    def test_inscription_invalid_username(self, client):
        """Test d'inscription avec nom d'utilisateur invalide"""
        response = client.post(
            "/api/v1/auth/inscription",
            json={
                "nom_utilisateur": "ab",
                "mot_de_passe": "password123"
            }
        )
        assert response.status_code == 422

    def test_connexion_success(self, client, test_user):
        """Test de connexion réussie"""
        response = client.post(
            "/api/v1/auth/connexion",
            json={
                "nom_utilisateur": "testuser",
                "mot_de_passe": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_connexion_wrong_password(self, client, test_user):
        """Test de connexion avec mauvais mot de passe"""
        response = client.post(
            "/api/v1/auth/connexion",
            json={
                "nom_utilisateur": "testuser",
                "mot_de_passe": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_connexion_nonexistent_user(self, client):
        """Test de connexion avec utilisateur inexistant"""
        response = client.post(
            "/api/v1/auth/connexion",
            json={
                "nom_utilisateur": "ghostuser",
                "mot_de_passe": "password123"
            }
        )
        assert response.status_code == 401


class TestAdminEndpoints:
    """Tests des endpoints d'administration"""

    def test_get_all_users_as_admin(self, client, admin_headers, test_user):
        """Test de récupération des utilisateurs en tant qu'admin"""
        response = client.get(
            "/api/v1/utilisateurs/admin/all",
            headers=admin_headers
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2

    def test_get_all_users_as_regular_user(self, client, auth_headers):
        """Test de récupération des utilisateurs sans privilèges admin"""
        response = client.get(
            "/api/v1/utilisateurs/admin/all",
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_get_all_users_unauthorized(self, client):
        """Test de récupération des utilisateurs sans authentification"""
        response = client.get("/api/v1/utilisateurs/admin/all")
        assert response.status_code == 401
