import { NavLink, useNavigate } from "react-router-dom";

import { apiClient } from "@/api/client";
import { useAuth } from "@/hooks/useAuth";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "rounded-md px-3 py-2 text-sm font-medium transition",
    isActive
      ? "bg-fg-mustard text-fg-navy-dark"
      : "text-fg-cream hover:bg-fg-navy-dark/60",
  ].join(" ");

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { user, refetch } = useAuth();
  const navigate = useNavigate();

  const onLogout = async () => {
    await apiClient.post("/logout");
    await refetch();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="bg-fg-navy text-fg-cream">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-8">
            <h1 className="text-lg font-semibold tracking-tight">
              Dashboard FG
            </h1>
            <nav className="flex gap-1">
              <NavLink to="/" end className={linkClass}>
                Produtividade
              </NavLink>
              <NavLink to="/ranking" className={linkClass}>
                Ranking
              </NavLink>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            {user?.picture && (
              <img
                src={user.picture}
                alt={user.name}
                className="h-8 w-8 rounded-full"
              />
            )}
            <span className="text-sm">{user?.name}</span>
            <button
              type="button"
              onClick={onLogout}
              className="btn btn-secondary border-fg-cream/30 !text-fg-cream hover:!bg-fg-navy-dark"
            >
              Sair
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-6">
        {children}
      </main>
    </div>
  );
}
