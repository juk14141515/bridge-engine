import { Navigate, Route, Routes } from "react-router-dom";
import { LandingPage } from "./pages/LandingPage";
import { SettingsPage } from "./pages/SettingsPage";
import { AppShell } from "./components/layout/AppShell";
import WorkspacePage from "./pages/WorkspacePage";
import HomePage from "./pages/HomePage";
import StartPage from "./pages/StartPage";

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/start" element={<StartPage />} />
        <Route path="/workspace/:workflowId" element={<WorkspacePage />} />
        {/* Legacy routes → current product flow */}
        <Route path="/app" element={<Navigate to="/start" replace />} />
        <Route path="/lanes" element={<Navigate to="/home" replace />} />
        <Route path="/task/new" element={<Navigate to="/start" replace />} />
        <Route path="/welcome" element={<Navigate to="/home" replace />} />
        <Route path="/new" element={<Navigate to="/start" replace />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
