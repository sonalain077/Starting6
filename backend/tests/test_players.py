"""Tests pour les endpoints des joueurs NBA"""
import pytest


class TestPlayers:
    """Tests des endpoints de gestion des joueurs"""

    def test_get_players_list(self, client, sample_players):
        """Test de récupération de la liste des joueurs"""
        response = client.get("/api/v1/players")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert isinstance(data["players"], list)

    def test_get_players_search_by_name(self, client, sample_players):
        """Test de recherche de joueurs par nom"""
        response = client.get("/api/v1/players?search=LeBron")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert isinstance(data["players"], list)
