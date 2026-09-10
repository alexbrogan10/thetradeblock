import { Fragment, useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { api } from "../services/api";
import type { DraftCapital } from "../types";

const ROUNDS = [1, 2, 3, 4, 5, 6, 7];

export function DraftCapitalPage() {
  const [data, setData] = useState<DraftCapital[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    api
      .getAllTeamsDraftCapital()
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="rounded border border-rose-300 bg-rose-50 p-4 text-rose-800">
        Failed to load draft capital: {error}
      </div>
    );
  }
  if (!data) {
    return <div className="text-slate-500">Loading Draft Capital Dashboard…</div>;
  }

  const years = Array.from(new Set(data.flatMap((d) => d.by_year.map((y) => y.year)))).sort();

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Draft Capital Dashboard</h1>
        <p className="text-sm text-slate-500">
          Estimated draft-pick value currently owned by each team, across all draft years on
          file. Click a team to see its breakdown by year and round.
        </p>
      </header>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                <th className="py-2">Team</th>
                <th className="text-right">Total Picks</th>
                <th className="text-right">Estimated Total Value</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <Fragment key={d.team.id}>
                  <tr
                    onClick={() => setExpanded(expanded === d.team.id ? null : d.team.id)}
                    className="cursor-pointer border-b border-slate-100 hover:bg-slate-50"
                  >
                    <td className="py-2 font-medium text-slate-800">
                      {expanded === d.team.id ? "▾" : "▸"} {d.team.name}
                    </td>
                    <td className="text-right text-slate-600">{d.total_picks}</td>
                    <td className="text-right font-semibold text-slate-800">
                      {d.estimated_total_value.toLocaleString()}
                    </td>
                  </tr>
                  {expanded === d.team.id && (
                    <tr className="border-b border-slate-100 bg-slate-50">
                      <td colSpan={3} className="px-4 py-3">
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                          {d.by_year.map((y) => (
                            <div key={y.year} className="rounded border border-slate-200 bg-white p-3">
                              <div className="mb-1 flex items-center justify-between">
                                <span className="font-semibold text-slate-700">{y.year} Draft</span>
                                <span className="text-xs text-slate-400">
                                  {y.estimated_value.toLocaleString()} pts
                                </span>
                              </div>
                              <ul className="space-y-0.5 text-xs text-slate-500">
                                {ROUNDS.map((r) => {
                                  const count = y.by_round[`round_${r}`] || 0;
                                  return count > 0 ? (
                                    <li key={r} className="flex justify-between">
                                      <span>Round {r}</span>
                                      <span>{count}</span>
                                    </li>
                                  ) : null;
                                })}
                              </ul>
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs text-slate-400">
        Draft years covered: {years.join(", ")}. Values are model estimates (average of three
        independent valuation curves — see Trade Center for methodology), not a claim of a
        team's actual draft strategy.
      </p>
    </div>
  );
}
