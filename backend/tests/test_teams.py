"""Tests pour la gestion des équipes fantasy"""
import pytest


class TestFantasyTeams:
    """Tests des endpoints de gestion d'équipes"""

    def test_create_team_unauthorized(self, client):
        """Test de création d'équipe sans authentification"""
        response = client.post(
            "/api/v1/teams/",
            json={"name": "Equipe Test"}
        )
        assert response.status_code == 401

    def test_get_my_team_empty(self, client, auth_headers):
        """Test de récupération de mes équipes (liste vide)"""
        response = client.get(
            "/api/v1/teams/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        teams = response.json()
        assert isinstance(teams, list)
