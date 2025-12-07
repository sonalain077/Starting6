'use client';

/**
 * PAGE DASHBOARD - Page protégée accessible uniquement aux utilisateurs connectés
 * 
 * Cette page affiche :
 * - Les infos de l'utilisateur
 * - Un bouton de déconnexion
 * - (À venir) Les stats de l'équipe, le leaderboard, etc.
 */

import { useAuth } from '@/context/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  // Redirige vers login si pas connecté
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Affiche rien pendant la redirection
  if (!isAuthenticated || !user) {
    return null;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="mx-auto max-w-4xl pt-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white">
              Dashboard 🏀
            </h1>
            <p className="mt-2 text-purple-200">
              Bienvenue, {user.nom_utilisateur} !
            </p>
          </div>

          <Button onClick={handleLogout} variant="outline">
            Se déconnecter
          </Button>
        </div>

        {/* Cards principales */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Mon Équipe</CardTitle>
              <CardDescription>Gère ton roster de 6 joueurs</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-sm text-muted-foreground">
                Compose ton roster de 6 joueurs avec un budget de $60M. Recrute des superstars et optimise ton équipe pour grimper au classement.
              </p>
              <Button className="w-full bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600" onClick={() => router.push('/team')}>
                🏀 Voir mon équipe
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Classement Solo League</CardTitle>
              <CardDescription>Ta position mondiale</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-sm text-muted-foreground">
                Consulte le leaderboard mondial et compare ton score avec les autres joueurs de la Solo League.
              </p>
              <Button className="w-full" onClick={() => router.push('/leaderboard')}>
                🏆 Voir le classement
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Informations du compte */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Informations du compte</CardTitle>
            <CardDescription>Tes données personnelles</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Username :</span>
              <span className="text-purple-400">{user.nom_utilisateur}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-semibold">Membre depuis :</span>
              <span>{new Date(user.date_creation).toLocaleDateString('fr-FR')}</span>
            </div>
          </CardContent>
        </Card>

        {/* Info technique */}
        <Card className="mt-8 border-yellow-500/50 bg-yellow-950/20">
          <CardHeader>
            <CardTitle className="text-yellow-400">✅ Authentification fonctionnelle !</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-yellow-200">
              Tu es actuellement connecté. Ton token JWT est stocké dans le localStorage et sera
              automatiquement inclus dans toutes les requêtes API.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
