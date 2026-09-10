import type { TeamAnalysis, TradeAnalysisResult } from "../types";

function triggerDownload(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function downloadTradeReportJSON(result: TradeAnalysisResult) {
  triggerDownload(JSON.stringify(result, null, 2), "trade-report.json", "application/json");
}

function csvEscape(value: unknown): string {
  const s = String(value ?? "");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function downloadTradeReportCSV(result: TradeAnalysisResult) {
  const rows: string[][] = [
    ["Team", "Direction", "Asset Type", "Asset", "Value"],
  ];
  for (const side of [result.team_a, result.team_b]) {
    for (const a of side.receives) rows.push([side.team_name, "Receives", a.asset_type, a.label, String(a.value)]);
    for (const a of side.gives) rows.push([side.team_name, "Gives", a.asset_type, a.label, String(a.value)]);
  }
  rows.push([]);
  rows.push(["Team", "Assessment", "Asset Value Delta", "Roster Fit", "Financial Impact ($M)", "Risk", "Timeline"]);
  for (const side of [result.team_a, result.team_b]) {
    rows.push([
      side.team_name,
      side.assessment,
      String(side.asset_value_delta),
      String(side.roster_fit_score),
      String(side.financial_impact),
      side.risk_level,
      side.competitive_window,
    ]);
  }
  rows.push([]);
  rows.push(["Overall Confidence", `${result.confidence}%`]);

  const csv = rows.map((r) => r.map(csvEscape).join(",")).join("\n");
  triggerDownload(csv, "trade-report.csv", "text/csv");
}

function teamReportHTML(side: TeamAnalysis): string {
  const assetRow = (label: string, value: number) =>
    `<tr><td>${label}</td><td style="text-align:right">${value}</td></tr>`;
  return `
    <div class="team-block">
      <h2>${side.team_name}</h2>
      <table class="assets">
        <tr><th>Receives</th><th>Gives</th></tr>
        <tr>
          <td>${side.receives.map((a) => `${a.label} (${a.value})`).join("<br/>") || "Nothing"}</td>
          <td>${side.gives.map((a) => `${a.label} (${a.value})`).join("<br/>") || "Nothing"}</td>
        </tr>
      </table>
      <table class="metrics">
        ${assetRow("Asset Value Delta", side.asset_value_delta)}
        ${assetRow("Roster Fit", Math.round(side.roster_fit_score - 50))}
        ${assetRow("Draft Capital Delta (pts)", Math.round(side.draft_capital_delta))}
        ${assetRow("Financial Impact ($M)", side.financial_impact)}
        <tr><td>Risk</td><td style="text-align:right">${side.risk_level}</td></tr>
        <tr><td>Competitive Window</td><td style="text-align:right">${side.competitive_window}</td></tr>
      </table>
      <p class="assessment">Assessment: <strong>${side.assessment}</strong></p>
      <h4>Why?</h4>
      <ul>${[...side.positive_drivers, ...side.negative_drivers].map((d) => `<li>${d}</li>`).join("")}</ul>
      <h4>What Could Change This?</h4>
      <ul>${side.what_could_change_this.map((d) => `<li>${d}</li>`).join("")}</ul>
    </div>
  `;
}

export function openPrintableTradeReport(result: TradeAnalysisResult) {
  const win = window.open("", "_blank", "width=900,height=1000");
  if (!win) return;

  const html = `
<!doctype html>
<html>
<head>
<title>Trade Analysis Report</title>
<meta charset="utf-8" />
<style>
  body { font-family: -apple-system, Segoe UI, Arial, sans-serif; color: #1e293b; margin: 2rem; }
  h1 { border-bottom: 2px solid #1e293b; padding-bottom: 0.5rem; }
  .disclaimer { font-size: 12px; font-style: italic; color: #64748b; margin-bottom: 1.5rem; }
  .team-block { border: 1px solid #cbd5e1; border-radius: 6px; padding: 1rem; margin-bottom: 1.5rem; page-break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 0.75rem; font-size: 13px; }
  table.assets td { vertical-align: top; border: 1px solid #e2e8f0; padding: 6px; width: 50%; }
  table.metrics td { border-bottom: 1px solid #f1f5f9; padding: 4px 2px; }
  .assessment { font-size: 15px; }
  h4 { margin-bottom: 0.25rem; }
  ul { margin-top: 0; font-size: 13px; }
  .confidence { font-size: 14px; margin-bottom: 1rem; }
  @media print { button { display: none; } }
</style>
</head>
<body>
  <h1>The Trade Block — Trade Analysis Report</h1>
  <p class="disclaimer">${result.disclaimer} Player model ${result.player_valuation_model_version} · Draft pick model ${result.draft_pick_model_version}.</p>
  <p class="confidence">Overall Confidence: <strong>${result.confidence}%</strong></p>
  ${teamReportHTML(result.team_a)}
  ${teamReportHTML(result.team_b)}
  <button onclick="window.print()">Print / Save as PDF</button>
</body>
</html>`;

  win.document.open();
  win.document.write(html);
  win.document.close();
}
