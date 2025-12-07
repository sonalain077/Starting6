"use client";

import { useEffect, useState } from "react";
import * as api from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, TrendingUp, DollarSign, Users, ChevronLeft, ChevronRight } from "lucide-react";
import { Player } from "@/lib/types";

const POSITIONS = ["ALL", "PG", "SG", "SF", "PF", "C"];
const NBA_TEAMS = [
  "ALL", "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
  "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC",
  "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
];

const SORT_OPTIONS = [
  { value: "name", label: "Nom (A-Z)" },
  { value: "score", label: "Score Moyen ↓" },
  { value: "price_asc", label: "Prix ↑" },
  { value: "price_desc", label: "Prix ↓" },
];

const ITEMS_PER_PAGE = 20;

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [filteredPlayers, setFilteredPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPosition, setSelectedPosition] = useState("ALL");
  const [selectedTeam, setSelectedTeam] = useState("ALL");
  const [sortBy, setSortBy] = useState("name");
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchPlayers();
  }, [searchQuery, selectedPosition, selectedTeam, sortBy]);

  const fetchPlayers = async () => {
    try {
      setLoading(true);
      
      // ✅ Préparer les paramètres pour l'API
      const params: any = { limit: 500 };
      
      if (selectedPosition !== "ALL") {
        params.position = selectedPosition;
      }
      
      if (selectedTeam !== "ALL") {
        params.team = selectedTeam;
      }
      
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }
      
      const response = await api.getPlayers(params);
      console.log("📊 Réponse API:", response);
      console.log("👥 Nombre de joueurs:", response.total);
      
      // Trier côté client car l'API ne gère pas tous les tris
      let sortedPlayers = [...(response.players || [])];
      
      switch (sortBy) {
        case "name":
          sortedPlayers.sort((a, b) => a.full_name.localeCompare(b.full_name));
          break;
        case "score":
          sortedPlayers.sort((a, b) => (b.avg_fantasy_score_last_15 || 0) - (a.avg_fantasy_score_last_15 || 0));
          break;
        case "price_asc":
          sortedPlayers.sort((a, b) => a.fantasy_cost - b.fantasy_cost);
          break;
        case "price_desc":
          sortedPlayers.sort((a, b) => b.fantasy_cost - a.fantasy_cost);
          break;
      }
      
      setPlayers(sortedPlayers);
      setFilteredPlayers(sortedPlayers);
      setTotalPages(Math.ceil(sortedPlayers.length / ITEMS_PER_PAGE));
      setCurrentPage(1);
    } catch (error) {
      console.error("❌ Erreur lors du chargement des joueurs:", error);
      setPlayers([]);
      setFilteredPlayers([]);
    } finally {
      setLoading(false);
    }
  };

  const getPaginatedPlayers = () => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return filteredPlayers.slice(startIndex, endIndex);
  };

  const getPositionColor = (position: string) => {
    const colors: Record<string, string> = {
      PG: "bg-blue-100 text-blue-700",
      SG: "bg-green-100 text-green-700",
      SF: "bg-yellow-100 text-yellow-700",
      PF: "bg-orange-100 text-orange-700",
      C: "bg-purple-100 text-purple-700",
    };
    return colors[position] || "bg-gray-100 text-gray-700";
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-orange-500 bg-clip-text text-transparent">
          🏀 Tous les Joueurs NBA
        </h1>
        <p className="text-gray-600 mt-2">
          {filteredPlayers.length} joueurs disponibles · Saison 2025-2026
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filtres & Recherche
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Rechercher un joueur (ex: LeBron James, Stephen Curry...)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filter Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Position Filter */}
            <div>
              <label className="text-sm font-medium mb-2 block">Position</label>
              <Select value={selectedPosition} onValueChange={setSelectedPosition}>
                <SelectTrigger>
                  <SelectValue placeholder="Toutes les positions" />
                </SelectTrigger>
                <SelectContent>
                  {POSITIONS.map((pos) => (
                    <SelectItem key={pos} value={pos}>
                      {pos === "ALL" ? "Toutes" : pos}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Team Filter */}
            <div>
              <label className="text-sm font-medium mb-2 block">Équipe NBA</label>
              <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                <SelectTrigger>
                  <SelectValue placeholder="Toutes les équipes" />
                </SelectTrigger>
                <SelectContent>
                  {NBA_TEAMS.map((team) => (
                    <SelectItem key={team} value={team}>
                      {team === "ALL" ? "Toutes" : team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div>
              <label className="text-sm font-medium mb-2 block">Trier par</label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SORT_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Reset Button */}
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedPosition("ALL");
                  setSelectedTeam("ALL");
                  setSortBy("name");
                }}
                className="w-full"
              >
                Réinitialiser
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Total</p>
                <p className="text-2xl font-bold">{filteredPlayers.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {POSITIONS.slice(1).map((pos) => {
          const count = filteredPlayers.filter((p) => p.player_position === pos).length;
          return (
            <Card key={pos}>
              <CardContent className="p-4">
                <Badge className={getPositionColor(pos)}>{pos}</Badge>
                <p className="text-2xl font-bold mt-2">{count}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Players Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {getPaginatedPlayers().map((player) => (
          <Card key={player.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <Badge className={getPositionColor(player.player_position)}>
                  {player.player_position}
                </Badge>
                <span className="text-xs font-semibold text-gray-600">
                  {player.team_abbreviation}
                </span>
              </div>
              <CardTitle className="text-lg mt-2">{player.full_name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  Prix
                </span>
                <span className="font-bold text-green-600">
                  ${(player.fantasy_cost / 1_000_000).toFixed(1)}M
                </span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  Score Moyen
                </span>
                <span className="font-bold text-purple-600">
                  {player.avg_fantasy_score_last_15?.toFixed(1) || "0.0"}
                </span>
              </div>

              <div className="pt-2 border-t">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Matchs joués (20j)</span>
                  <span className="font-semibold">
                    {player.games_played_last_20 || 0}
                  </span>
                </div>
              </div>

              {player.is_injured && (
                <Badge variant="destructive" className="w-full justify-center">
                  🩹 Blessé
                </Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Précédent
              </Button>

              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  Page {currentPage} sur {totalPages}
                </span>
                <span className="text-xs text-gray-500">
                  ({filteredPlayers.length} résultats)
                </span>
              </div>

              <Button
                variant="outline"
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Suivant
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Results */}
      {filteredPlayers.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg text-gray-600">Aucun joueur trouvé</p>
            <p className="text-sm text-gray-500 mt-2">
              Essayez de modifier vos critères de recherche
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
