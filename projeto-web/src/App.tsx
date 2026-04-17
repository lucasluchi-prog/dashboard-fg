import { Navigate, Route, Routes } from "react-router-dom";

import AppShell from "@/components/AppShell";
import { useAuth } from "@/hooks/useAuth";
import Dashboard from "@/routes/Dashboard";
import Login from "@/routes/Login";
import Ranking from "@/routes/Ranking";

function Protected({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="p-8">Carregando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <AppShell>
              <Dashboard />
            </AppShell>
          </Protected>
        }
      />
      <Route
        path="/ranking"
        element={
          <Protected>
            <AppShell>
              <Ranking />
            </AppShell>
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
