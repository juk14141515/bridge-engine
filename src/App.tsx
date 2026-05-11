import { Navigate, Route, Routes } from "react-router-dom";
import { LandingPage } from "./pages/LandingPage";
import { AppPage } from "./pages/AppPage";
import { SettingsPage } from "./pages/SettingsPage";
import { AppShell } from "./components/layout/AppShell";
import { LanesPage } from "./pages/LanesPage";
import { NewTaskPage } from "./pages/NewTaskPage";
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
        {/* Legacy routes kept so older links keep working */}
        <Route path="/app" element={<AppPage />} />
        <Route path="/lanes" element={<LanesPage />} />
        <Route path="/task/new" element={<NewTaskPage />} />
        <Route path="/new" element={<Navigate to="/start" replace />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
