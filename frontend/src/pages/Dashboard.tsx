import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "../components/common/Card";
import { ScoreBadge } from "../components/common/ScoreBadge";
import { api } from "../services/api";
import type { DashboardOverview } from "../types";

export function Dashboard() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getDashboard()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="rounded border border-rose-300 bg-rose-50 p-4 text-rose-800">
        Failed to load dashboard: {error}. Is the backend running and seeded?
      </div>
    );
  }
  if (!data) {
    return <div className="text-slate-500">Loading Front Office Dashboard…</div>;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Front Office Dashboard</h1>
        <p className="text-sm text-slate-500">
          Executive overview of the current analytical environment. All figures are
          model estimates for decision support — not predictions of actual trades.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Highest Estimated Trade Value">
          <ul className="divide-y divide-slate-100">
            {data.trade_market.highest_value_players.map((p) => (
              <li key={p.player_id} className="flex items-center justify-between py-2 text-sm">
                <div>
                  <span className="font-medium text-slate-800">{p.name}</span>{" "}
                  <span className="text-slate-400">
                    {p.position} · {p.team}
                  </span>
                </div>
                <ScoreBadge score={p.valuation} />
              </li>
            ))}
            {data.trade_market.highest_value_players.length === 0 && (
              <li className="py-4 text-sm text-slate-400">No player data loaded yet.</li>
            )}
          </ul>
        </Card>

        <Card title="Positions Commanding High Trade Value">
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={data.trade_market.positions_commanding_value}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="position" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="average_valuation" fill="#0ea5e9" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Teams With Significant Future Draft Capital">
          <ul className="divide-y divide-slate-100">
            {data.team_opportunities.draft_capital_by_team.map((t) => (
              <li key={t.team_id} className="flex items-center justify-between py-2 text-sm">
                <span className="font-medium text-slate-800">{t.team}</span>
                <span className="text-slate-500">
                  {t.pick_count} picks · {t.estimated_total_value.toLocaleString()} pts
                </span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Teams With Limited Draft Capital">
          <ul className="divide-y divide-slate-100">
            {data.team_opportunities.limited_draft_capital_teams.map((t) => (
              <li key={t.team_id} className="flex items-center justify-between py-2 text-sm">
                <span className="font-medium text-slate-800">{t.team}</span>
                <span className="text-slate-500">
                  {t.pick_count} picks · {t.estimated_total_value.toLocaleString()} pts
                </span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Model Alerts" className="lg:col-span-2">
          <ul className="space-y-2">
            {data.model_alerts.map((alert, i) => (
              <li key={i} className="rounded bg-slate-50 px-3 py-2 text-sm text-slate-700">
                {alert}
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Potential Trade Value Discrepancies" className="lg:col-span-2">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                <th className="py-2">Player</th>
                <th>Position</th>
                <th>Team</th>
                <th>Analytical Value</th>
                <th>Expected (Cost-Implied)</th>
                <th>Potential Discrepancy</th>
              </tr>
            </thead>
            <tbody>
              {data.value_discrepancies.map((d) => (
                <tr key={d.player_id} className="border-b border-slate-100">
                  <td className="py-2 font-medium text-slate-800">{d.name}</td>
                  <td>{d.position}</td>
                  <td>{d.team}</td>
                  <td>{d.analytical_value}</td>
                  <td>{d.expected_value_for_cost}</td>
                  <td className={d.potential_discrepancy > 0 ? "text-emerald-600" : "text-rose-600"}>
                    {d.potential_discrepancy > 0 ? "+" : ""}
                    {d.potential_discrepancy}
                  </td>
                </tr>
              ))}
              {data.value_discrepancies.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-slate-400">
                    No significant discrepancies identified from current data.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <p className="mt-3 text-xs text-slate-400">
            The model identifies potential value discrepancies between analytical player
            value and what current contract cost would imply — not a claim that any
            player is objectively over- or under-valued.
          </p>
        </Card>
      </div>
    </div>
  );
}
