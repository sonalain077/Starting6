'use client';

/**
 * PAGE "MON ÉQUIPE"
 * 
 * Cette page affiche :
 * 1. Si pas d'équipe → Formulaire de création
 * 2. Si équipe existe → Roster avec les 6 joueurs
 * 
 * Architecture :
 * - useEffect pour charger les équipes au montage
 * - État local pour stocker l'équipe et le roster
 * - Affichage conditionnel selon l'état
 */

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import AddPlayerModal from '@/components/AddPlayerModal';
import * as api from '@/lib/api';
import type { FantasyTeam, RosterPlayer } from '@/lib/types';

export default function TeamPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // ============================================================================
  // ÉTATS
  // ============================================================================

  const [myTeam, setMyTeam] = useState<FantasyTeam | null>(null);
  const [roster, setRoster] = useState<RosterPlayer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [teamName, setTeamName] = useState('');
  const [error, setError] = useState('');
  
  // États pour la modale
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [playerToReplace, setPlayerToReplace] = useState<number | null>(null);
  const [isRemoving, setIsRemoving] = useState(false);

  // ============================================================================
  // PROTECTION DE LA ROUTE
  // ============================================================================

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // ============================================================================
  // CHARGEMENT DES DONNÉES
  // ============================================================================

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadTeam = async () => {
      try {
        setIsLoading(true);
        
        // 1. Récupérer mes équipes
        const myTeams = await api.getMyTeam();
        
        if (myTeams && myTeams.length > 0) {
          // Prendre la première équipe (pour l'instant)
          const team = myTeams[0];
          setMyTeam(team);
          
          // 2. Récupérer le roster de cette équipe
          const rosterData = await api.getMyRoster(team.id);
          setRoster(rosterData.roster || []);
        }
      } catch (err: any) {
        console.error('Erreur chargement équipe:', err);
        // Si pas d'équipe, c'est normal, on affiche le formulaire de création
      } finally {
        setIsLoading(false);
      }
    };

    loadTeam();
  }, [isAuthenticated]);

  // ============================================================================
  // CRÉATION D'ÉQUIPE
  // ============================================================================

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (teamName.length < 3) {
      setError('Le nom doit contenir au moins 3 caractères');
      return;
    }

    setIsCreating(true);

    try {
      // Créer l'équipe dans la Solo League (league_id = 1)
      const newTeam = await api.createTeam({
        name: teamName,
        league_id: 1, // Solo League par défaut
      });

      setMyTeam(newTeam);
      setTeamName('');
      
      // Recharger le roster (vide pour l'instant)
      const rosterData = await api.getMyRoster(newTeam.id);
      setRoster(rosterData.roster || []);
    } catch (err: any) {
      console.error('Erreur création équipe:', err);
      setError(err.message || "Impossible de créer l'équipe");
    } finally {
      setIsCreating(false);
    }
  };

  // ============================================================================
  // GESTION DE LA MODALE
  // ============================================================================

  const handleOpenModal = (positionSlot: string, playerId?: number) => {
    setSelectedSlot(positionSlot);
    setPlayerToReplace(playerId || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedSlot('');
    setPlayerToReplace(null);
  };

  const handlePlayerAdded = async () => {
    // Recharger le roster après ajout ou remplacement
    if (myTeam) {
      const rosterData = await api.getMyRoster(myTeam.id);
      setRoster(rosterData.roster || []);
      
      // Mettre à jour aussi le salary cap de l'équipe
      setMyTeam({
        ...myTeam,
        salary_cap_used: rosterData.salary_cap_used,
      });
    }
  };

  // ============================================================================
  // RETIRER UN JOUEUR
  // ============================================================================

  const handleRemovePlayer = async (playerId: number) => {
    if (!myTeam) return;

    // Confirmation
    if (!confirm('Es-tu sûr de vouloir retirer ce joueur de ton équipe ?')) {
      return;
    }

    try {
      setIsRemoving(true);
      setError('');

      const response = await fetch(
        `http://localhost:8000/api/v1/teams/${myTeam.id}/roster/${playerId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${api.getToken()}`,
          },
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Impossible de retirer le joueur');
      }

      // Succès - recharger le roster
      const rosterData = await api.getMyRoster(myTeam.id);
      setRoster(rosterData.roster || []);
      
      setMyTeam({
        ...myTeam,
        salary_cap_used: rosterData.salary_cap_used,
      });
    } catch (err: any) {
      console.error('Erreur retrait joueur:', err);
      alert(err.message);
    } finally {
      setIsRemoving(false);
    }
  };

  // ============================================================================
  // HELPERS
  // ============================================================================

  const formatMoney = (amount: number) => {
    return `$${(amount / 1_000_000).toFixed(1)}M`;
  };

  const getPositionLabel = (slot: string) => {
    const labels: Record<string, string> = {
      PG: 'Meneur',
      SG: 'Arrière',
      SF: 'Ailier',
      PF: 'Ailier Fort',
      C: 'Pivot',
      UTIL: 'Sixième Homme',
    };
    return labels[slot] || slot;
  };

  // ============================================================================
  // AFFICHAGE PENDANT LE CHARGEMENT
  // ============================================================================

  if (!isAuthenticated || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-white border-t-transparent"></div>
          <p className="mt-4 text-white">Chargement...</p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // AFFICHAGE SI PAS D'ÉQUIPE → FORMULAIRE DE CRÉATION
  // ============================================================================

  if (!myTeam) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
        <div className="mx-auto max-w-2xl pt-16">
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-5xl font-bold text-white">
              Crée ton équipe 🏀
            </h1>
            <p className="mt-4 text-xl text-purple-200">
              Choisis un nom pour ton équipe et commence à recruter les meilleurs joueurs NBA !
            </p>
          </div>

          {/* Card de création */}
          <Card>
            <CardHeader>
              <CardTitle>Nouvelle équipe</CardTitle>
              <CardDescription>
                Ton équipe sera créée dans la Solo League (compétition globale)
              </CardDescription>
            </CardHeader>

            <form onSubmit={handleCreateTeam}>
              <CardContent className="space-y-4">
                {error && (
                  <div className="rounded-lg bg-destructive/15 p-3 text-sm text-destructive">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="teamName">Nom de l'équipe</Label>
                  <Input
                    id="teamName"
                    type="text"
                    placeholder="Les Warriors du 77"
                    value={teamName}
                    onChange={(e) => setTeamName(e.target.value)}
                    required
                    disabled={isCreating}
                    maxLength={50}
                  />
                  <p className="text-xs text-muted-foreground">
                    Minimum 3 caractères, maximum 50
                  </p>
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isCreating}
                >
                  {isCreating ? 'Création...' : 'Créer mon équipe'}
                </Button>
              </CardContent>
            </form>
          </Card>

          {/* Infos */}
          <Card className="mt-6 border-blue-500/50 bg-blue-950/20">
            <CardContent className="pt-6">
              <h3 className="mb-2 font-semibold text-blue-400">📋 Règles du jeu</h3>
              <ul className="space-y-1 text-sm text-blue-200">
                <li>• Compose une équipe de <strong>6 joueurs</strong> (PG, SG, SF, PF, C, UTIL)</li>
                <li>• Budget total : <strong>$60M</strong></li>
                <li>• Maximum <strong>2 transferts par semaine</strong></li>
                <li>• Scores mis à jour quotidiennement</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // ============================================================================
  // AFFICHAGE SI ÉQUIPE EXISTE → ROSTER
  // ============================================================================

  const salaryCap = myTeam.salary_cap_used || 0;
  const salaryCapRemaining = 60_000_000 - salaryCap;
  const salaryCapPercentage = (salaryCap / 60_000_000) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="mx-auto max-w-6xl pt-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-purple-200 hover:text-white"
          >
            ← Retour au dashboard
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white">
                {myTeam.name}
              </h1>
              <p className="mt-2 text-purple-200">
                Solo League
              </p>
            </div>

            <Button variant="outline">
              Renommer l'équipe
            </Button>
          </div>
        </div>

        {/* Stats de l'équipe */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">💰 Salary Cap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatMoney(salaryCap)} / $60M
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-200">
                <div
                  className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                  style={{ width: `${salaryCapPercentage}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Restant : {formatMoney(salaryCapRemaining)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">📊 Score Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {myTeam.total_score?.toFixed(1) || '0.0'} pts
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Mis à jour quotidiennement
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">🏆 Classement</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                #{myTeam.rank || '—'}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Position globale
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Roster - Les 6 joueurs */}
        <Card>
          <CardHeader>
            <CardTitle>Mon Roster</CardTitle>
            <CardDescription>
              Compose ton équipe de 6 joueurs respectant les positions
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {roster.map((slot) => (
                <Card key={slot.position_slot} className="overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-bold">
                        {slot.position_slot}
                      </CardTitle>
                      <span className="text-xs text-muted-foreground">
                        {getPositionLabel(slot.position_slot)}
                      </span>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-4">
                    {slot.player ? (
                      <>
                        <div className="mb-2">
                          <div className="font-semibold">
                            {slot.player.first_name} {slot.player.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {slot.player.team} • {slot.player.player_position}
                          </div>
                        </div>

                        <div className="mb-3 flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Coût :</span>
                          <span className="font-semibold">
                            {formatMoney(slot.acquired_salary || slot.player.fantasy_cost)}
                          </span>
                        </div>

                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="flex-1"
                            onClick={() => slot.player && handleOpenModal(slot.position_slot, slot.player.id)}
                            disabled={isRemoving || !slot.player}
                          >
                            Remplacer
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive" 
                            className="flex-1"
                            onClick={() => slot.player && handleRemovePlayer(slot.player.id)}
                            disabled={isRemoving || !slot.player}
                          >
                            Retirer
                          </Button>
                        </div>
                      </>
                    ) : (
                      <div className="py-8 text-center">
                        <div className="mb-3 text-4xl opacity-30">👤</div>
                        <Button 
                          size="sm" 
                          className="w-full"
                          onClick={() => handleOpenModal(slot.position_slot)}
                        >
                          Ajouter un joueur
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Modale d'ajout/remplacement de joueur */}
        {myTeam && (
          <AddPlayerModal
            isOpen={isModalOpen}
            onClose={handleCloseModal}
            teamId={myTeam.id}
            positionSlot={selectedSlot}
            playerToReplace={playerToReplace}
            onPlayerAdded={handlePlayerAdded}
          />
        )}
      </div>
    </div>
  );
}
