import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/layout/Sidebar";
import { DemoBanner } from "./components/layout/DemoBanner";
import { Dashboard } from "./pages/Dashboard";
import { TradeCenter } from "./pages/TradeCenter";
import { DraftCapitalPage } from "./pages/DraftCapital";
import { ScenariosPage } from "./pages/Scenarios";
import { TradeFinderPage } from "./pages/TradeFinder";
import { ValueDiscrepanciesPage } from "./pages/ValueDiscrepancies";
import { api } from "./services/api";

export default function App() {
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    api
      .getDashboard()
      .then((d) => setDemoMode(d.demo_mode))
      .catch(() => {});
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <DemoBanner visible={demoMode} />
        <main className="flex-1 overflow-y-auto bg-slate-100 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trade-center" element={<TradeCenter />} />
            <Route path="/draft-capital" element={<DraftCapitalPage />} />
            <Route path="/scenarios" element={<ScenariosPage />} />
            <Route path="/trade-finder" element={<TradeFinderPage />} />
            <Route path="/value-discrepancies" element={<ValueDiscrepanciesPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
