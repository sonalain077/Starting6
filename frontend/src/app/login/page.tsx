'use client';

/**
 * PAGE LOGIN - Connexion des utilisateurs
 * 
 * Cette page permet aux utilisateurs de se connecter avec leur username + password.
 * Après une connexion réussie, ils sont redirigés vers le dashboard.
 * 
 * Utilise le AuthContext (useAuth) pour gérer l'authentification.
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  // ============================================================================
  // ÉTAT DU FORMULAIRE
  // ============================================================================

  const [formData, setFormData] = useState({
    nom_utilisateur: '',
    mot_de_passe: '',
  });

  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // GESTION DES CHAMPS
  // ============================================================================

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Efface l'erreur dès que l'utilisateur commence à taper
    if (error) setError('');
  };

  // ============================================================================
  // SOUMISSION DU FORMULAIRE
  // ============================================================================

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Empêche le rechargement de la page
    setError('');
    setIsLoading(true);

    try {
      // Appelle la fonction login du AuthContext
      await login(formData.nom_utilisateur, formData.mot_de_passe);
      
      // Si succès, redirige vers le dashboard
      router.push('/dashboard');
    } catch (err: any) {
      // Si échec, affiche l'erreur
      console.error('Login error:', err);
      setError(err.message || 'Identifiants incorrects');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // RENDU
  // ============================================================================

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold text-center">
            Starting Six 🏀
          </CardTitle>
          <CardDescription className="text-center">
            Connecte-toi pour gérer ton équipe de rêve
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {/* Message d'erreur */}
            {error && (
              <div className="rounded-lg bg-destructive/15 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            {/* Champ Username */}
            <div className="space-y-2">
              <Label htmlFor="nom_utilisateur">Nom d'utilisateur</Label>
              <Input
                id="nom_utilisateur"
                name="nom_utilisateur"
                type="text"
                placeholder="ton_pseudo"
                value={formData.nom_utilisateur}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>

            {/* Champ Password */}
            <div className="space-y-2">
              <Label htmlFor="mot_de_passe">Mot de passe</Label>
              <Input
                id="mot_de_passe"
                name="mot_de_passe"
                type="password"
                placeholder="••••••••"
                value={formData.mot_de_passe}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            {/* Bouton de connexion */}
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </Button>

            {/* Lien vers la page Register */}
            <p className="text-center text-sm text-muted-foreground">
              Pas encore de compte ?{' '}
              <Link
                href="/register"
                className="font-medium text-primary hover:underline"
              >
                Inscris-toi ici
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
