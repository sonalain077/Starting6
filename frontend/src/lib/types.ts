// 🎯 Types TypeScript - Correspondent aux schémas Pydantic du backend

// ============================================================================
// AUTH TYPES
// ============================================================================

export interface LoginRequest {
  nom_utilisateur: string;
  mot_de_passe: string;
}

export interface RegisterRequest {
  nom_utilisateur: string;
  mot_de_passe: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  nom_utilisateur: string;
  date_creation: string;
}

// ============================================================================
// PLAYER TYPES
// ============================================================================

export interface Player {
  id: number;
  external_api_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  player_position: string; // "PG" | "SG" | "SF" | "PF" | "C"
  team: string;
  team_abbreviation: string;
  jersey_number: string | null;
  height: string | null;
  weight: string | null;
  fantasy_cost: number; // Coût en dollars
  avg_fantasy_score_last_15: number | null;
  games_played_last_20: number | null;
  is_injured: boolean;
  injury_status: string | null;
  is_active: boolean;
}

export interface PlayerListResponse {
  players: Player[];
  total: number;
  skip: number;
  limit: number;
  filters_applied?: Record<string, any>;
}

export interface PlayerGameScore {
  id: number;
  player_id: number;
  game_date: string;
  opponent: string;
  minutes_played: number;
  points: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  fantasy_score: number;
}

// ============================================================================
// TEAM TYPES
// ============================================================================

export type RosterSlot = "PG" | "SG" | "SF" | "PF" | "C" | "UTIL";

export interface FantasyTeam {
  id: number;
  name: string;
  owner_id: number;
  league_id: number;
  salary_cap_used: number;
  waiver_priority: number | null;
  transfers_this_week: number;
  is_roster_complete: number; // 0 ou 1 (boolean en DB)
  total_score: number | null;
  rank: number | null;
  date_creation: string;
  last_updated: string;
}

export interface RosterPlayer {
  position_slot: RosterSlot;
  player: Player | null;
  acquired_salary: number | null;
  date_acquired: string | null;
}

export interface TeamScore {
  fantasy_team_id: number;
  score_date: string;
  total_score: number;
  players_who_played: number;
}

// ============================================================================
// LEAGUE TYPES
// ============================================================================

export interface League {
  id: number;
  name: string;
  type: "SOLO" | "PRIVATE";
  commissioner_id: number | null;
  max_teams: number;
  salary_cap: number;
  is_active: boolean;
  start_date: string;
  end_date: string | null;
}

export interface LeaderboardEntry {
  team_id: number;
  team_name: string;
  owner_username: string;
  total_score: number;
  last_7_days_score: number;
  games_played: number;
  average_score: number;
  trend: "up" | "down" | "stable";
  rank: number;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiError {
  detail: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}
