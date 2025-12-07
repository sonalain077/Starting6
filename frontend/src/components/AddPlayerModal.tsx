'use client';

/**
 * COMPOSANT : Modal d'ajout de joueur
 * 
 * Permet de :
 * - Parcourir les joueurs NBA disponibles
 * - Filtrer par poste
 * - Rechercher par nom
 * - Ajouter un joueur à une position spécifique du roster
 */

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import * as api from '@/lib/api';
import type { Player } from '@/lib/types';

interface AddPlayerModalProps {
  isOpen: boolean;
  onClose: () => void;
  teamId: number;
  positionSlot: string;
  playerToReplace?: number | null;
  onPlayerAdded: () => void;
}

interface AvailablePlayer {
  player: Player;
  is_affordable: boolean;
  has_cooldown: boolean;
  cost: number;
}

export default function AddPlayerModal({
  isOpen,
  onClose,
  teamId,
  positionSlot,
  playerToReplace,
  onPlayerAdded,
}: AddPlayerModalProps) {
  // ============================================================================
  // ÉTATS
  // ============================================================================

  const [players, setPlayers] = useState<AvailablePlayer[]>([]);
  const [filteredPlayers, setFilteredPlayers] = useState<AvailablePlayer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [search, setSearch] = useState('');
  const [positionFilter, setPositionFilter] = useState<string>('ALL');
  const [error, setError] = useState('');

  // ============================================================================
  // CHARGEMENT DES JOUEURS
  // ============================================================================

  useEffect(() => {
    if (!isOpen) return;

    const loadPlayers = async () => {
      try {
        setIsLoading(true);
        setError('');

        // Appel API pour récupérer les joueurs disponibles
        const data = await api.getAvailablePlayers(teamId, {
          limit: 100
        });
        
        setPlayers(data.players || []);
        setFilteredPlayers(data.players || []);
      } catch (err: any) {
        console.error('Erreur chargement joueurs:', err);
        setError(err.message || 'Impossible de charger les joueurs');
      } finally {
        setIsLoading(false);
      }
    };

    loadPlayers();
  }, [isOpen, teamId]);

  // ============================================================================
  // FILTRAGE DES JOUEURS
  // ============================================================================

  useEffect(() => {
    let filtered = [...players];

    // Filtre par recherche (nom)
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.player.first_name.toLowerCase().includes(searchLower) ||
          p.player.last_name.toLowerCase().includes(searchLower) ||
          `${p.player.first_name} ${p.player.last_name}`
            .toLowerCase()
            .includes(searchLower)
      );
    }

    // Filtre par poste
    if (positionFilter !== 'ALL') {
      filtered = filtered.filter((p) => p.player.player_position === positionFilter);
    }

    setFilteredPlayers(filtered);
  }, [search, positionFilter, players]);

  // ============================================================================
  // AJOUT D'UN JOUEUR
  // ============================================================================

  const handleAddPlayer = async (playerId: number) => {
    try {
      setIsAdding(true);
      setError('');

      // Si on remplace un joueur, on doit d'abord le retirer
      if (playerToReplace) {
        const deleteResponse = await fetch(
          `http://localhost:8000/api/v1/teams/${teamId}/roster/${playerToReplace}`,
          {
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${api.getToken()}`,
            },
          }
        );

        if (!deleteResponse.ok) {
          const error = await deleteResponse.json();
          throw new Error(error.detail || 'Impossible de retirer l\'ancien joueur');
        }
      }

      // Puis ajouter le nouveau joueur
      const response = await fetch(
        `http://localhost:8000/api/v1/teams/${teamId}/roster`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${api.getToken()}`,
          },
          body: JSON.stringify({
            player_id: playerId,
            position_slot: positionSlot,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Impossible d\'ajouter le joueur');
      }

      // Succès !
      onPlayerAdded();
      onClose();
    } catch (err: any) {
      console.error('Erreur ajout/remplacement joueur:', err);
      setError(err.message);
    } finally {
      setIsAdding(false);
    }
  };

  // ============================================================================
  // HELPERS
  // ============================================================================

  const formatMoney = (amount: number) => {
    return `$${(amount / 1_000_000).toFixed(1)}M`;
  };

  const getPositionColor = (pos: string) => {
    const colors: Record<string, string> = {
      PG: 'bg-blue-500',
      SG: 'bg-green-500',
      SF: 'bg-yellow-500',
      PF: 'bg-orange-500',
      C: 'bg-red-500',
    };
    return colors[pos] || 'bg-gray-500';
  };

  // ============================================================================
  // RENDU
  // ============================================================================

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>
            {playerToReplace ? 'Remplacer' : 'Ajouter'} un joueur - {positionSlot}
          </DialogTitle>
          <DialogDescription>
            {playerToReplace 
              ? `Sélectionne un nouveau joueur pour remplacer l'actuel`
              : `Sélectionne un joueur pour la position ${positionSlot}`
            }
          </DialogDescription>
        </DialogHeader>

        {/* Filtres */}
        <div className="flex gap-4 py-4">
          <Input
            placeholder="Rechercher un joueur..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1"
          />

          <Select value={positionFilter} onValueChange={setPositionFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Poste" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous</SelectItem>
              <SelectItem value="PG">PG</SelectItem>
              <SelectItem value="SG">SG</SelectItem>
              <SelectItem value="SF">SF</SelectItem>
              <SelectItem value="PF">PF</SelectItem>
              <SelectItem value="C">C</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="rounded-lg bg-destructive/15 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Liste des joueurs */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
          ) : filteredPlayers.length === 0 ? (
            <div className="flex h-48 items-center justify-center text-muted-foreground">
              Aucun joueur trouvé
            </div>
          ) : (
            <div className="space-y-2">
              {filteredPlayers.map((item) => {
                const player = item.player;
                const canAfford = item.is_affordable;
                const hasCooldown = item.has_cooldown;

                return (
                  <div
                    key={player.id}
                    className={`flex items-center justify-between rounded-lg border p-4 transition-colors ${
                      canAfford && !hasCooldown
                        ? 'hover:bg-accent'
                        : 'opacity-50'
                    }`}
                  >
                    {/* Info joueur */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">
                          {player.first_name} {player.last_name}
                        </span>
                        <Badge
                          className={`${getPositionColor(player.player_position)} text-white`}
                        >
                          {player.player_position}
                        </Badge>
                        {player.is_injured && (
                          <Badge variant="destructive">Blessé</Badge>
                        )}
                      </div>

                      <div className="mt-1 text-sm text-muted-foreground">
                        {player.team}
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="mx-4 text-right">
                      <div className="font-semibold">
                        {formatMoney(player.fantasy_cost)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Avg: {player.avg_fantasy_score_last_15?.toFixed(1) || '0.0'}
                      </div>
                    </div>

                    {/* Bouton */}
                    <Button
                      size="sm"
                      onClick={() => handleAddPlayer(player.id)}
                      disabled={!canAfford || hasCooldown || isAdding}
                    >
                      {hasCooldown
                        ? 'Cooldown'
                        : !canAfford
                        ? 'Trop cher'
                        : 'Ajouter'}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
