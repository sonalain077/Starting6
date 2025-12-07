"""Tests pour le système de calcul de scores fantasy"""
import pytest


def calculate_fantasy_score(stats: dict) -> float:
    """Fonction de calcul de score fantasy (à adapter selon votre implémentation)"""
    score = 0.0
    
    # Points de base
    score += stats.get('pts', 0) * 1.0
    score += stats.get('reb', 0) * 1.2
    score += stats.get('ast', 0) * 1.5
    score += stats.get('stl', 0) * 3.0
    score += stats.get('blk', 0) * 3.0
    score -= stats.get('to', 0) * 1.5
    score -= stats.get('pf', 0) * 0.5
    
    # Bonus d'efficacité FG%
    fga = stats.get('fga', 0)
    fgm = stats.get('fgm', 0)
    if fga >= 10:
        fg_pct = fgm / fga if fga > 0 else 0
        if fg_pct >= 0.60:
            score += 3
    
    # Bonus 3-points
    if stats.get('fg3m', 0) >= 3:
        score += 2
    
    # Détection double-double et triple-double
    double_stats = sum([
        stats.get('pts', 0) >= 10,
        stats.get('reb', 0) >= 10,
        stats.get('ast', 0) >= 10,
        stats.get('stl', 0) >= 10,
        stats.get('blk', 0) >= 10,
    ])
    
    if double_stats == 2:
        score += 5
    elif double_stats == 3:
        score += 12
    elif double_stats >= 4:
        score += 25
    
    # Pénalités
    if fga >= 15 and (fgm / fga if fga > 0 else 0) < 0.30:
        score -= 3
    
    if stats.get('to', 0) >= 5:
        score -= 2
    
    if stats.get('pf', 0) >= 6:
        score -= 5
    
    return round(score, 1)


class TestFantasyScoring:
    """Tests du moteur de calcul de points fantasy"""

    def test_basic_scoring(self):
        """Test du calcul de base (points, rebonds, passes)"""
        stats = {
            'pts': 25,
            'reb': 8,
            'ast': 6,
            'stl': 1,
            'blk': 0,
            'to': 2,
            'pf': 3,
            'fgm': 10,
            'fga': 20,
            'fg3m': 2,
            'ftm': 5,
            'fta': 6
        }
        score = calculate_fantasy_score(stats)
        
        # 25*1.0 + 8*1.2 + 6*1.5 + 1*3.0 + 0*3.0 - 2*1.5 - 3*0.5
        expected = 25 + 9.6 + 9 + 3 - 3 - 1.5
        assert abs(score - expected) < 0.5

    def test_double_double_bonus(self):
        """Test du bonus double-double"""
        stats = {
            'pts': 12,
            'reb': 11,
            'ast': 4,
            'stl': 1,
            'blk': 0,
            'to': 2,
            'pf': 2,
            'fgm': 5,
            'fga': 10,
            'fg3m': 0,
            'ftm': 2,
            'fta': 2
        }
        score = calculate_fantasy_score(stats)
        
        # Devrait inclure +5 pour le double-double (10+ pts et 10+ reb)
        assert score > (12 + 11*1.2 + 4*1.5 + 3 - 3 - 1)

    def test_triple_double_bonus(self):
        """Test du bonus triple-double"""
        stats = {
            'pts': 15,
            'reb': 12,
            'ast': 10,
            'stl': 2,
            'blk': 1,
            'to': 3,
            'pf': 2,
            'fgm': 6,
            'fga': 12,
            'fg3m': 1,
            'ftm': 2,
            'fta': 2
        }
        score = calculate_fantasy_score(stats)
        
        # Devrait inclure +12 pour le triple-double
        base = (15 + 12*1.2 + 10*1.5 + 2*3 + 1*3 - 3*1.5 - 2*0.5)
        assert score > base + 10

    def test_efficiency_bonus(self):
        """Test des bonus d'efficacité (FG%, 3PT)"""
        stats = {
            'pts': 20,
            'reb': 5,
            'ast': 3,
            'stl': 0,
            'blk': 0,
            'to': 1,
            'pf': 1,
            'fgm': 12,
            'fga': 15,
            'fg3m': 4,
            'ftm': 2,
            'fta': 2
        }
        score = calculate_fantasy_score(stats)
        
        # Devrait inclure +3 (FG%) et +2 (3PT)
        base = 20 + 5*1.2 + 3*1.5 - 1*1.5 - 1*0.5
        assert score > base + 4

    def test_negative_score_possible(self):
        """Test qu'un score négatif est possible en cas de très mauvaise perf"""
        stats = {
            'pts': 2,
            'reb': 1,
            'ast': 0,
            'stl': 0,
            'blk': 0,
            'to': 8,
            'pf': 6,
            'fgm': 1,
            'fga': 15,
            'fg3m': 0,
            'ftm': 0,
            'fta': 0
        }
        score = calculate_fantasy_score(stats)
        
        # Devrait être négatif
        assert score < 0
