"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { Home, Trophy, Users, User, LogOut, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Navigation() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navItems = [
    { href: "/dashboard", label: "Tableau de bord", icon: Home },
    { href: "/team", label: "Mon Équipe", icon: Users },
    { href: "/leaderboard", label: "Classement", icon: Trophy },
  ];
  
  // Ajouter le lien admin si l'utilisateur est admin
  if (user?.is_admin) {
    navItems.push({ href: "/admin", label: "Administration", icon: Shield });
  }

  const isActive = (href: string) => pathname === href;

  if (!user) return null;

  return (
    <nav className="bg-white border-b shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-orange-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">S6</span>
            </div>
            <div className="hidden md:block">
              <h1 className="font-bold text-xl bg-gradient-to-r from-purple-600 to-orange-500 bg-clip-text text-transparent">
                Starting Six
              </h1>
              <p className="text-xs text-gray-500">NBA Fantasy League</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={active ? "default" : "ghost"}
                    className={`gap-2 ${
                      active
                        ? "bg-gradient-to-r from-purple-600 to-orange-500 text-white"
                        : "hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden md:inline">{item.label}</span>
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-3">
            <div className="hidden md:block text-right">
              <p className="text-sm font-semibold">{user.nom_utilisateur}</p>
              <p className="text-xs text-gray-500">
                {user.is_admin ? "👑 Administrateur" : "Membre"}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={logout}
              className="gap-2 text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden md:inline">Déconnexion</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
