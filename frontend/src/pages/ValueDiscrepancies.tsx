import { useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { api } from "../services/api";
import type { ValueDiscrepancy } from "../types";

const POSITIONS = ["", "QB", "RB", "WR", "TE", "OT", "IOL", "EDGE", "DT", "LB", "CB", "S", "K", "P", "LS"];

export function ValueDiscrepanciesPage() {
  const [minDiscrepancy, setMinDiscrepancy] = useState(12);
  const [position, setPosition] = useState("");
  const [results, setResults] = useState<ValueDiscrepancy[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api
      .getValueDiscrepancies({ min_discrepancy: minDiscrepancy, position: position || undefined })
      .then(setResults)
      .catch((e) => setError(e.message));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Trade Value Discrepancy Finder</h1>
        <p className="text-sm text-slate-500">
          Compares analytical player value against an expected-cost proxy derived from each
          player's own contract. The model identifies a potential value discrepancy — this is
          not a claim that any player is objectively over- or under-valued.
        </p>
      </header>

      <Card title="Filters">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Minimum |Discrepancy|</label>
            <input
              type="number"
              className="w-28 rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={minDiscrepancy}
              onChange={(e) => setMinDiscrepancy(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Position</label>
            <select
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
            >
              {POSITIONS.map((p) => (
                <option key={p} value={p}>
                  {p || "All"}
                </option>
              ))}
            </select>
          </div>
          <button onClick={load} className="rounded bg-slate-900 px-4 py-1.5 text-sm font-semibold text-white">
            Apply
          </button>
        </div>
      </Card>

      {error && <div className="rounded border border-rose-300 bg-rose-50 p-3 text-sm text-rose-800">{error}</div>}

      {results && (
        <Card title={`Results (${results.length})`}>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                <th className="py-2">Player</th>
                <th>Position</th>
                <th>Team</th>
                <th>Analytical Value</th>
                <th>Expected (Cost-Implied)</th>
                <th>Potential Discrepancy</th>
                <th>Drivers</th>
              </tr>
            </thead>
            <tbody>
              {results.map((d) => (
                <tr key={d.player_id} className="border-b border-slate-100 align-top">
                  <td className="py-2 font-medium text-slate-800">{d.name}</td>
                  <td>{d.position}</td>
                  <td>{d.team}</td>
                  <td>{d.analytical_value}</td>
                  <td>{d.expected_value_for_cost}</td>
                  <td className={d.potential_discrepancy > 0 ? "font-semibold text-emerald-600" : "font-semibold text-rose-600"}>
                    {d.potential_discrepancy > 0 ? "+" : ""}
                    {d.potential_discrepancy}
                  </td>
                  <td className="text-xs text-slate-500">{d.drivers.join("; ")}</td>
                </tr>
              ))}
              {results.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-4 text-center text-slate-400">
                    No discrepancies found for these filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
