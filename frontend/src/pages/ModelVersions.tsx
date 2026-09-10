import { useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { api } from "../services/api";
import type { ModelVersion } from "../types";

export function ModelVersionsPage() {
  const [versions, setVersions] = useState<ModelVersion[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getModelVersions()
      .then(setVersions)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return <div className="rounded border border-rose-300 bg-rose-50 p-4 text-sm text-rose-800">{error}</div>;
  }
  if (!versions) {
    return <div className="text-slate-500">Loading model versions…</div>;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Model Versions</h1>
        <p className="text-sm text-slate-500">
          Every model behind The Trade Block — heuristic and machine-learned — is versioned so a
          trade scenario computed with it stays auditable even after the model changes (Section
          39-40). Model outputs are estimates, not facts.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {versions.map((v) => (
          <Card key={v.id} title={`${v.model_name} — ${v.version}`}>
            <div className="space-y-2 text-sm">
              <div className="text-xs text-slate-400">
                Trained/registered: {new Date(v.training_date).toLocaleString()} · Dataset:{" "}
                {v.dataset_version}
              </div>
              <div>
                <span className="font-semibold text-slate-600">Features: </span>
                {v.features.join(", ")}
              </div>
              <div>
                <span className="font-semibold text-slate-600">Parameters: </span>
                <code className="text-xs">{JSON.stringify(v.parameters)}</code>
              </div>
              {Object.keys(v.evaluation_metrics).length > 0 && (
                <div>
                  <span className="font-semibold text-slate-600">Evaluation metrics: </span>
                  {Object.entries(v.evaluation_metrics)
                    .map(([k, val]) => `${k}=${val}`)
                    .join(", ")}
                </div>
              )}
              {v.limitations.length > 0 && (
                <div>
                  <span className="font-semibold text-slate-600">Limitations:</span>
                  <ul className="mt-1 list-inside list-disc text-xs text-slate-500">
                    {v.limitations.map((l, i) => (
                      <li key={i}>{l}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
