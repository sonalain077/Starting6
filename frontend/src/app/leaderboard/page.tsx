"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";
import * as api from "@/lib/api";
import type { LeaderboardEntry } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Trophy, Medal, TrendingUp, Users } from "lucide-react";

export default function LeaderboardPage() {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [myTeamRank, setMyTeamRank] = useState<number | null>(null);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await api.getSoloLeaderboard();
      
      setLeaderboard(data);
      
      // Trouver le rang de mon équipe
      if (user) {
        const myTeam = data.find((team) => team.owner_username === user.nom_utilisateur);
        if (myTeam) {
          setMyTeamRank(myTeam.rank);
        }
      }
    } catch (error) {
      console.error("Erreur lors du chargement du leaderboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-8 h-8 text-yellow-500" />;
      case 2:
        return <Medal className="w-8 h-8 text-gray-400" />;
      case 3:
        return <Medal className="w-8 h-8 text-amber-600" />;
      default:
        return <span className="text-2xl font-bold text-gray-600">#{rank}</span>;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case "down":
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
      default:
        return <span className="text-gray-400">—</span>;
    }
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-orange-500 bg-clip-text text-transparent">
            🏆 Classement Solo League
          </h1>
          <p className="text-gray-600 mt-2">
            Compétition mondiale - Tous les joueurs
          </p>
        </div>
        
        {myTeamRank && (
          <Card className="bg-gradient-to-br from-purple-50 to-orange-50">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Users className="w-6 h-6 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Votre position</p>
                  <p className="text-2xl font-bold text-purple-600">#{myTeamRank}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Équipes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{leaderboard.length}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Leader Actuel</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-yellow-500">
              {leaderboard[0]?.team_name || "—"}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {leaderboard[0]?.total_score.toFixed(1)} pts
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Score Moyen</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-600">
              {leaderboard.length > 0
                ? (leaderboard.reduce((sum, t) => sum + t.average_score, 0) / leaderboard.length).toFixed(1)
                : "0"}
            </p>
            <p className="text-sm text-gray-600 mt-1">pts/jour</p>
          </CardContent>
        </Card>
      </div>

      {/* Leaderboard Table */}
      <Card>
        <CardHeader>
          <CardTitle>🏅 Classement Général</CardTitle>
          <CardDescription>
            Mise à jour quotidienne après les matchs NBA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {leaderboard.map((team) => {
              const isMyTeam = user && team.owner_username === user.nom_utilisateur;
              
              return (
                <div
                  key={team.team_id}
                  className={`flex items-center gap-4 p-4 rounded-lg border-2 transition-all hover:shadow-md ${
                    isMyTeam
                      ? "bg-gradient-to-r from-purple-50 to-orange-50 border-purple-400"
                      : "bg-white border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {/* Rank */}
                  <div className="flex items-center justify-center w-16">
                    {getRankIcon(team.rank)}
                  </div>

                  {/* Team Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-lg">{team.team_name}</h3>
                      {isMyTeam && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">
                          Votre équipe
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      Manager : {team.owner_username}
                    </p>
                  </div>

                  {/* Stats */}
                  <div className="hidden md:flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <p className="text-gray-600">7 derniers jours</p>
                      <p className="font-semibold text-purple-600">
                        {team.last_7_days_score.toFixed(1)} pts
                      </p>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-gray-600">Moyenne</p>
                      <p className="font-semibold">
                        {team.average_score.toFixed(1)} pts/j
                      </p>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-gray-600">Tendance</p>
                      <div className="flex justify-center">
                        {getTrendIcon(team.trend)}
                      </div>
                    </div>
                  </div>

                  {/* Total Score */}
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Score Total</p>
                    <p className="text-2xl font-bold text-orange-500">
                      {team.total_score.toFixed(1)}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {leaderboard.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">Aucune équipe dans le classement</p>
              <p className="text-sm">Créez votre équipe pour apparaître ici !</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Legend */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-yellow-500" />
              <span>1ère place</span>
            </div>
            <div className="flex items-center gap-2">
              <Medal className="w-4 h-4 text-gray-400" />
              <span>2ème place</span>
            </div>
            <div className="flex items-center gap-2">
              <Medal className="w-4 h-4 text-amber-600" />
              <span>3ème place</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span>Tendance à la hausse</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
              <span>Tendance à la baisse</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
