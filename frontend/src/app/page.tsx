'use client';

/**
 * PAGE D'ACCUEIL
 * 
 * Landing page simple qui présente le projet et redirige vers login/register
 */

import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // Si déjà connecté, redirige vers le dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-2xl text-center">
        {/* Logo / Titre */}
        <h1 className="mb-4 text-6xl font-bold text-white">
          Starting Six 🏀
        </h1>

        {/* Tagline */}
        <p className="mb-8 text-xl text-purple-200">
          Compose ton équipe de rêve et affronte les meilleurs managers de la NBA Fantasy League
        </p>

        {/* Features */}
        <div className="mb-12 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-white/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">📊</div>
            <h3 className="mb-1 font-semibold text-white">Scores en temps réel</h3>
            <p className="text-sm text-purple-200">
              Statistiques mises à jour chaque jour
            </p>
          </div>

          <div className="rounded-lg bg-white/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">💰</div>
            <h3 className="mb-1 font-semibold text-white">Salary Cap</h3>
            <p className="text-sm text-purple-200">
              Gère ton budget de 60M$ intelligemment
            </p>
          </div>

          <div className="rounded-lg bg-white/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">🏆</div>
            <h3 className="mb-1 font-semibold text-white">Classement Global</h3>
            <p className="text-sm text-purple-200">
              Compare-toi aux autres managers
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Button asChild size="lg" className="text-lg">
            <Link href="/register">
              Créer mon équipe
            </Link>
          </Button>

          <Button asChild size="lg" variant="outline" className="text-lg">
            <Link href="/login">
              Se connecter
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
