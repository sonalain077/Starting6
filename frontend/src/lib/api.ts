// 🚀 API CLIENT - Pont entre Frontend et Backend
// Ce fichier contient TOUTES les fonctions pour parler au backend

import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  Player,
  PlayerListResponse,
  PlayerGameScore,
  FantasyTeam,
  RosterPlayer,
  TeamScore,
  League,
  LeaderboardEntry,
  ApiError,
} from './types';

// ============================================================================
// CONFIGURATION
// ============================================================================

// URL du backend (change selon l'environnement)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';
const BASE_URL = `${API_BASE_URL}${API_VERSION}`;

// ============================================================================
// HELPERS - Fonctions utilitaires
// ============================================================================

/**
 * Récupère le token JWT stocké dans localStorage
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Stocke le token JWT dans localStorage
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', token);
}

/**
 * Supprime le token JWT de localStorage
 */
export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
}

/**
 * Fonction générique pour faire des requêtes HTTP
 * @param endpoint - L'endpoint de l'API (ex: "/players")
 * @param options - Options de la requête (method, body, etc.)
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const token = getToken();

  // Headers par défaut
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Ajoute le token si disponible
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Si erreur HTTP (4xx, 5xx)
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP Error: ${response.status} ${response.statusText}`,
      }));
      
      // Assurer que error.detail est bien une string
      const errorMessage = typeof error.detail === 'string' 
        ? error.detail 
        : JSON.stringify(error.detail) || `HTTP Error: ${response.status}`;
      
      throw new Error(errorMessage);
    }

    // Si succès, retourne les données
    return await response.json();
  } catch (error) {
    // Gestion des erreurs réseau ou parsing
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Une erreur inconnue est survenue');
  }
}

// ============================================================================
// 🔐 AUTHENTIFICATION
// ============================================================================

/**
 * Connexion utilisateur
 * POST /auth/connexion
 */
export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await fetchAPI<AuthResponse>('/auth/connexion', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });

  // Stocke le token pour les futures requêtes
  setToken(response.access_token);

  return response;
}

/**
 * Inscription utilisateur
 * POST /auth/inscription
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await fetchAPI<AuthResponse>('/auth/inscription', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Stocke le token automatiquement
  setToken(response.access_token);

  return response;
}

/**
 * Déconnexion
 */
export function logout(): void {
  removeToken();
  // Redirige vers la page de login (fait depuis le composant)
}

/**
 * Récupère l'utilisateur actuel
 * GET /utilisateurs/me
 */
export async function getCurrentUser(): Promise<User> {
  return fetchAPI<User>('/utilisateurs/me');
}

// ============================================================================
// 👥 JOUEURS NBA
// ============================================================================

/**
 * Liste tous les joueurs NBA
 * GET /players
 */
export async function getPlayers(params?: {
  position?: string;
  team?: string;
  search?: string;
  limit?: number;
}): Promise<PlayerListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.position) queryParams.append('position', params.position);
  if (params?.team) queryParams.append('team', params.team);
  if (params?.search) queryParams.append('search', params.search);
  // Par défaut, récupérer TOUS les joueurs (500 max, largement suffisant)
  queryParams.append('limit', (params?.limit || 500).toString());

  const query = queryParams.toString();
  return fetchAPI<PlayerListResponse>(`/players${query ? `?${query}` : ''}`);
}

/**
 * Détails d'un joueur spécifique
 * GET /players/{player_id}
 */
export async function getPlayer(playerId: number): Promise<Player> {
  return fetchAPI<Player>(`/players/${playerId}`);
}

/**
 * Scores d'un joueur
 * GET /players/{player_id}/scores
 */
export async function getPlayerScores(
  playerId: number,
  limit: number = 10
): Promise<PlayerGameScore[]> {
  return fetchAPI<PlayerGameScore[]>(
    `/players/${playerId}/scores?limit=${limit}`
  );
}

// ============================================================================
// 🏀 MON ÉQUIPE
// ============================================================================

/**
 * Récupère toutes mes équipes
 * GET /teams/me
 */
export async function getMyTeam(): Promise<FantasyTeam[]> {
  return fetchAPI<FantasyTeam[]>('/teams/me');
}

/**
 * Créer une nouvelle équipe
 * POST /teams
 */
export async function createTeam(data: {
  name: string;
  league_id: number;
}): Promise<FantasyTeam> {
  return fetchAPI<FantasyTeam>('/teams', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Récupère le roster d'une équipe (6 joueurs)
 * GET /teams/{team_id}/roster
 */
export async function getMyRoster(teamId: number): Promise<{
  roster: RosterPlayer[];
  salary_cap_used: number;
  salary_cap_remaining: number;
  roster_status: string;
  is_roster_complete: boolean;
  transfers_this_week: number;
}> {
  return fetchAPI(`/teams/${teamId}/roster`);
}

/**
 * Récupère les joueurs disponibles pour une équipe
 * GET /teams/{team_id}/available-players
 */
export async function getAvailablePlayers(
  teamId: number,
  params?: {
    position?: string;
    team_nba?: string;
    max_salary?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }
): Promise<{
  players: Array<{
    player: Player;
    is_affordable: boolean;
    has_cooldown: boolean;
    cost: number;
  }>;
  total: number;
  salary_cap_remaining: number;
}> {
  const queryParams = new URLSearchParams();
  if (params?.position) queryParams.append('position', params.position);
  if (params?.team_nba) queryParams.append('team_nba', params.team_nba);
  if (params?.max_salary) queryParams.append('max_salary', params.max_salary.toString());
  if (params?.search) queryParams.append('search', params.search);
  if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
  if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
  
  const query = queryParams.toString();
  return fetchAPI(`/teams/${teamId}/available-players${query ? `?${query}` : ''}`);
}

/**
 * Ajoute un joueur au roster
 * POST /roster/add/{player_id}
 */
export async function addPlayerToRoster(data: {
  player_id: number;
  roster_slot: string;
}): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>('/roster/add', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Remplace un joueur du roster
 * POST /roster/replace
 */
export async function replacePlayer(data: {
  old_player_id: number;
  new_player_id: number;
}): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>('/roster/replace', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Retire un joueur du roster
 * DELETE /roster/remove/{player_id}
 */
export async function removePlayerFromRoster(
  playerId: number
): Promise<{ message: string }> {
  return fetchAPI<{ message: string }>(`/roster/remove/${playerId}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// 📊 SCORES & STATISTIQUES
// ============================================================================

/**
 * Scores de mon équipe
 * GET /scores/team
 */
export async function getMyTeamScores(params?: {
  start_date?: string;
  end_date?: string;
}): Promise<TeamScore[]> {
  const queryParams = new URLSearchParams();
  if (params?.start_date) queryParams.append('start_date', params.start_date);
  if (params?.end_date) queryParams.append('end_date', params.end_date);

  const query = queryParams.toString();
  return fetchAPI<TeamScore[]>(`/scores/team${query ? `?${query}` : ''}`);
}

/**
 * Score détaillé d'un jour spécifique
 * GET /scores/team/{date}
 */
export async function getTeamScoreByDate(date: string): Promise<{
  team_score: number;
  players: Array<{
    player: Player;
    score: number;
  }>;
}> {
  return fetchAPI(`/scores/team/${date}`);
}

// ============================================================================
// 🏆 CLASSEMENT & LIGUES
// ============================================================================

/**
 * Récupère toutes les ligues
 * GET /leagues
 */
export async function getLeagues(): Promise<League[]> {
  return fetchAPI<League[]>('/leagues');
}

/**
 * Détails d'une ligue
 * GET /leagues/{league_id}
 */
export async function getLeague(leagueId: number): Promise<League> {
  return fetchAPI<League>(`/leagues/${leagueId}`);
}

/**
 * Classement SOLO league
 * GET /leagues/solo/leaderboard
 */
export async function getSoloLeaderboard(): Promise<LeaderboardEntry[]> {
  return fetchAPI<LeaderboardEntry[]>('/leagues/solo/leaderboard');
}

/**
 * Classement d'une ligue privée
 * GET /leagues/{league_id}/leaderboard
 */
export async function getLeagueLeaderboard(
  leagueId: number
): Promise<LeaderboardEntry[]> {
  return fetchAPI<LeaderboardEntry[]>(`/leagues/${leagueId}/leaderboard`);
}

// ============================================================================
// 🔄 EXPORT DEFAULT
// ============================================================================

const api = {
  // Auth
  login,
  register,
  logout,
  getCurrentUser,

  // Players
  getPlayers,
  getPlayer,
  getPlayerScores,

  // Team
  getMyTeam,
  createTeam,
  getMyRoster,
  addPlayerToRoster,
  replacePlayer,
  removePlayerFromRoster,

  // Scores
  getMyTeamScores,
  getTeamScoreByDate,

  // Leagues
  getLeagues,
  getLeague,
  getSoloLeaderboard,
  getLeagueLeaderboard,
};

export default api;
