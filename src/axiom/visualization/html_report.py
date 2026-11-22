"""Institutional HTML report generator with clean responsive styling."""
import os
from typing import Dict, Any, List

class HTMLReportGenerator:
    @staticmethod
    def generate(
        title: str,
        asset_or_task: str,
        summary: str,
        confidence_level: str,
        confidence_reason: str,
        key_metrics: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        sources: List[Dict[str, str]],
        assumptions: List[str],
        limitations: List[str],
        charts: List[str],
        output_filepath: str
    ) -> str:
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

        chart_html = ""
        for c in charts:
            rel_c = os.path.basename(c)
            chart_html += f"""
            <div class="chart-card">
                <img src="charts/{rel_c}" alt="{rel_c}" class="chart-img"/>
            </div>
            """

        metrics_html = ""
        for k, v in key_metrics.items():
            k_clean = k.replace("_", " ").title()
            val_str = f"{v:.2f}" if isinstance(v, float) else str(v)
            metrics_html += f"""
            <div class="metric-card">
                <div class="metric-title">{k_clean}</div>
                <div class="metric-val">{val_str}</div>
            </div>
            """

        scenarios_html = ""
        for s in scenarios:
            chg = s.get("projected_change_pct", 0)
            chg_color = "#ef476f" if chg < 0 else "#06d6a0"
            scenarios_html += f"""
            <tr>
                <td><strong>{s.get('scenario')}</strong></td>
                <td style="color: {chg_color}; font-weight: bold;">{chg:+.2f}%</td>
                <td>${s.get('projected_price', 0):.2f}</td>
                <td>{s.get('mechanism', '')}</td>
            </tr>
            """

        sources_html = ""
        for src in sources:
            sources_html += f"""
            <tr>
                <td><strong>{src.get('name', 'Source')}</strong></td>
                <td><a href="{src.get('url', '#')}" target="_blank">{src.get('url', '-')}</a></td>
                <td><span class="badge badge-delayed">{src.get('freshness', 'DELAYED')}</span></td>
                <td>{src.get('observation_date', '-')}</td>
                <td>{src.get('retrieval_time_utc', '-')}</td>
            </tr>
            """

        assumptions_html = "".join([f"<li>{a}</li>" for a in assumptions])
        limitations_html = "".join([f"<li>{l}</li>" for l in limitations])

        html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — AXIOM AI AGENTS</title>
    <style>
        :root {{
            --bg: #0e1117;
            --surface: #161b22;
            --surface-border: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-cyan: #00b4d8;
            --accent-green: #06d6a0;
            --accent-gold: #ffd166;
            --accent-red: #ef476f;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-primary);
            line-height: 1.6;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .brand-badge {{
            display: inline-block;
            background: #1f6feb;
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        h1 {{
            font-size: 28px;
            margin: 8px 0;
            color: #ffffff;
        }}
        .meta-subtitle {{
            color: var(--text-secondary);
            font-size: 13px;
        }}
        .grid-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        .metric-card {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-title {{
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .metric-val {{
            font-size: 24px;
            font-weight: bold;
            color: var(--accent-cyan);
            margin-top: 6px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .card h2 {{
            font-size: 18px;
            margin-top: 0;
            color: #ffffff;
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 10px;
        }}
        .confidence-badge {{
            display: inline-block;
            background: #238636;
            color: #ffffff;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin: 12px 0;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--surface-border);
        }}
        th {{
            color: var(--text-secondary);
            font-weight: 600;
        }}
        .badge-delayed {{
            background: #8957e5;
            color: #fff;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }}
        .chart-img {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid var(--surface-border);
            margin: 16px 0;
        }}
        .disclaimer-box {{
            background: rgba(239, 71, 111, 0.08);
            border-left: 4px solid var(--accent-red);
            padding: 16px;
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 40px;
            border-radius: 0 8px 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand-badge">AXIOM AI AGENTS — Institutional Research</div>
            <h1>{title}</h1>
            <div class="meta-subtitle">Asset/Task: <strong>{asset_or_task}</strong> | Engine: Deterministic Python Core | Verification: Audited</div>
        </header>

        <div class="card">
            <h2>Executive Summary</h2>
            <p>{summary}</p>
            <div style="margin-top: 14px;">
                Tingkat Keyakinan: <span class="confidence-badge">{confidence_level.upper()}</span>
                <span style="margin-left: 10px; color: var(--text-secondary); font-size: 13px;">{confidence_reason}</span>
            </div>
        </div>

        <div class="grid-metrics">
            {metrics_html}
        </div>

        {chart_html}

        <div class="card">
            <h2>Analisis Skenario & Stress Testing</h2>
            <table>
                <thead>
                    <tr>
                        <th>Skenario Shock</th>
                        <th>Dampak Estimasi</th>
                        <th>Proyeksi Harga</th>
                        <th>Mekanisme Transmisi</th>
                    </tr>
                </thead>
                <tbody>
                    {scenarios_html}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Sumber Data & Atribusi</h2>
            <table>
                <thead>
                    <tr>
                        <th>Provider</th>
                        <th>Endpoint / Referensi</th>
                        <th>Status Kesegaran</th>
                        <th>Observasi</th>
                        <th>Waktu Retrieval (UTC)</th>
                    </tr>
                </thead>
                <tbody>
                    {sources_html}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Asumsi Metodologi & Keterbatasan</h2>
            <h3>Asumsi:</h3>
            <ul>{assumptions_html}</ul>
            <h3>Keterbatasan:</h3>
            <ul>{limitations_html}</ul>
        </div>

        <div class="disclaimer-box">
            <strong>Pernyataan Kepatuhan Institusional:</strong> Dokumen dan analisis ini dibuat secara otomatis oleh sistem riset AXIOM AI AGENTS semata-mata untuk kebutuhan analisa kuantitatif dan edukasi finansial. AXIOM bukan penasihat investasi berlisensi (financial advisor), tidak melakukan eksekusi order riil, dan tidak memberikan anjuran atau rekomendasi beli/jual instrumen keuangan. Keputusan alokasi modal dan risiko investasi sepenuhnya berada di tangan pengguna.
        </div>
    </div>
</body>
</html>
"""
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return output_filepath
