'use client';

/**
 * PAGE ADMIN - Gestion des Utilisateurs
 * 
 * Simple page pour gérer les droits administrateur des utilisateurs
 */

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/auth-context';
import { useRouter } from 'next/navigation';
import { getAllUsers, promoteUserToAdmin, demoteAdminToUser } from '@/lib/api';
import { User } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AdminPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Rediriger si non connecté
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Rediriger si non admin
    if (user && !user.is_admin) {
      router.push('/dashboard');
      return;
    }

    loadUsers();
  }, [user, isAuthenticated, router]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const users = await getAllUsers();
      setUsers(users);
    } catch (err: any) {
      console.error('Erreur chargement utilisateurs:', err);
      setError(err.message || err.response?.data?.detail || 'Erreur lors du chargement des utilisateurs');
    } finally {
      setLoading(false);
    }
  };

  const handlePromote = async (userId: number, username: string) => {
    if (!confirm(`Promouvoir "${username}" en administrateur ?`)) return;

    try {
      await promoteUserToAdmin(userId);
      await loadUsers(); // Recharger la liste
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erreur lors de la promotion');
    }
  };

  const handleDemote = async (userId: number, username: string) => {
    if (!confirm(`Rétrograder "${username}" en utilisateur normal ?`)) return;

    try {
      await demoteAdminToUser(userId);
      await loadUsers(); // Recharger la liste
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erreur lors de la rétrogradation');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-lg">Chargement...</p>
      </div>
    );
  }

  if (!user?.is_admin) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle>Accès Refusé</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Vous devez être administrateur pour accéder à cette page.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">🛡️ Administration</h1>
        <p className="text-gray-600">Gestion des utilisateurs et des droits</p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Utilisateurs de la Plateforme</CardTitle>
          <CardDescription>
            {users.length} utilisateur{users.length > 1 ? 's' : ''} enregistré{users.length > 1 ? 's' : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="p-3 text-left">ID</th>
                  <th className="p-3 text-left">Nom d'utilisateur</th>
                  <th className="p-3 text-left">Inscription</th>
                  <th className="p-3 text-left">Rôle</th>
                  <th className="p-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{u.id}</td>
                    <td className="p-3 font-medium">{u.nom_utilisateur}</td>
                    <td className="p-3 text-sm text-gray-600">
                      {new Date(u.date_creation).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="p-3">
                      {u.is_admin ? (
                        <span className="rounded-full bg-purple-100 px-3 py-1 text-sm font-semibold text-purple-800">
                          Admin
                        </span>
                      ) : (
                        <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-800">
                          Utilisateur
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      {u.is_admin ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDemote(u.id, u.nom_utilisateur)}
                          disabled={u.id === user.id}
                        >
                          Rétrograder
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handlePromote(u.id, u.nom_utilisateur)}
                        >
                          Promouvoir Admin
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8">
        <Button variant="outline" onClick={() => router.push('/dashboard')}>
          ← Retour au Dashboard
        </Button>
      </div>
    </div>
  );
}
