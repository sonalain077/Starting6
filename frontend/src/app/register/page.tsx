'use client';

/**
 * PAGE REGISTER - Inscription des nouveaux utilisateurs
 * 
 * Cette page permet aux nouveaux utilisateurs de créer un compte.
 * Après inscription réussie, ils sont automatiquement connectés et redirigés vers le dashboard.
 * 
 * Validations :
 * - Username : minimum 3 caractères
 * - Email : format valide
 * - Password : minimum 8 caractères
 * - Password confirmation : doit correspondre
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();

  // ============================================================================
  // ÉTAT DU FORMULAIRE
  // ============================================================================

  const [formData, setFormData] = useState({
    nom_utilisateur: '',
    mot_de_passe: '',
    confirmPassword: '',
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
    if (error) setError('');
  };

  // ============================================================================
  // VALIDATION CLIENT-SIDE
  // ============================================================================

  const validateForm = (): string | null => {
    if (formData.nom_utilisateur.length < 3) {
      return "Le nom d'utilisateur doit contenir au moins 3 caractères";
    }

    if (formData.mot_de_passe.length < 6) {
      return "Le mot de passe doit contenir au moins 6 caractères";
    }

    if (formData.mot_de_passe !== formData.confirmPassword) {
      return "Les mots de passe ne correspondent pas";
    }

    return null;
  };

  // ============================================================================
  // SOUMISSION DU FORMULAIRE
  // ============================================================================

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation côté client
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);

    try {
      // Appelle la fonction register du AuthContext
      await register(formData.nom_utilisateur, formData.mot_de_passe);
      
      // Si succès, redirige vers le dashboard
      router.push('/dashboard');
    } catch (err: any) {
      // Si échec, affiche l'erreur du backend
      console.error('Register error:', err);
      setError(err.message || "Une erreur s'est produite lors de l'inscription");
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
            Rejoins Starting Six 🏀
          </CardTitle>
          <CardDescription className="text-center">
            Crée ton compte et compose ton équipe de rêve
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
              <p className="text-xs text-muted-foreground">
                Minimum 3 caractères
              </p>
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
              <p className="text-xs text-muted-foreground">
                Minimum 6 caractères
              </p>
            </div>

            {/* Champ Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirme ton mot de passe</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            {/* Bouton d'inscription */}
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? "Inscription..." : "Créer mon compte"}
            </Button>

            {/* Lien vers la page Login */}
            <p className="text-center text-sm text-muted-foreground">
              Déjà un compte ?{' '}
              <Link
                href="/login"
                className="font-medium text-primary hover:underline"
              >
                Connecte-toi ici
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
