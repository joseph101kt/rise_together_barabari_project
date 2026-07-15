import React from "react";
import { Link, NavLink } from "react-router-dom";
import Logo from "./Logo";
import { Button } from "./ui/button";
import { useAuth } from "../context/AuthContext";
import { User, LogOut, LogIn, ArrowRight } from "lucide-react";

export function AppShell({ children }) {
  const { currentUser, logout, isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sticky nav */}
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <Logo />

          {/* Desktop nav links */}
          <nav className="hidden items-center gap-6 text-sm font-medium md:flex">
            <NavLink
              to="/learning-paths"
              className={({ isActive }) =>
                isActive
                  ? "text-[color:var(--brand-indigo)] font-bold text-lg"
                  : "text-foreground/80 transition-colors text-[color:var(--brand-indigo)] font-bold text-lg"
              }
            >
              Learning Paths
            </NavLink>
          </nav>

          {/* CTA buttons */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link
                  to={`/profile/${currentUser.id}`}
                  className="flex items-center gap-2 text-sm font-semibold text-[color:var(--brand-indigo)] hover:opacity-90"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--brand-indigo)]/10 text-[color:var(--brand-indigo)] shadow-sm">
                    <User className="h-4.5 w-4.5" />
                  </div>
                  <span className="hidden sm:inline font-sans text-lg font-semibold">{currentUser.name}</span>
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 font-semibold text-red-500 bg-red-500/10 rounded-xl px-3 py-1.5 border border-red-500/10 text-xs cursor-pointer select-none transition-all"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline text-sm font-semibold">Log out</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm" className="flex items-center gap-1.5 font-semibold">
                    <LogIn className="h-4 w-4" /> Sign in
                  </Button>
                </Link>
                <Link to="/register">
                  <Button
                    size="sm"
                    className="flex items-center gap-1.5 rounded-lg font-semibold text-white transition-transform hover:scale-[1.02]"
                    style={{ background: "var(--gradient-button)" }}
                  >
                    Get started <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main>{children}</main>

      <footer className="border-t border-border/50 bg-slate-50 py-8 mt-auto">
        <div className="mx-auto max-w-6xl px-6 text-center text-lg font-semibold text-[color:var(--brand-indigo)]">
          Rise Together · A Barabari Collective project
        </div>
      </footer>
    </div>
  );
}

export default AppShell;

