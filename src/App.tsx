import { Navigate, Route, Routes } from "react-router-dom";
import { LandingPage } from "./pages/LandingPage";
import { AppPage } from "./pages/AppPage";
import { SettingsPage } from "./pages/SettingsPage";
import { AppShell } from "./components/layout/AppShell";
import { LanesPage } from "./pages/LanesPage";
import { NewTaskPage } from "./pages/NewTaskPage";
import { WorkspacePage } from "./pages/WorkspacePage";

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<AppPage />} />
        <Route path="/lanes" element={<LanesPage />} />
        <Route path="/task/new" element={<NewTaskPage />} />
        <Route path="/workspace/:workflowId" element={<WorkspacePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}

