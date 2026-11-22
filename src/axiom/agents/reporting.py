"""Reporting Agent: Institutional synthesis, Markdown/HTML generation, and run packaging."""
import os
import json
import csv
import datetime
from typing import Dict, Any, List, Optional
from axiom.visualization.html_report import HTMLReportGenerator

class ReportingAgent:
    def __init__(self, reports_root: str = "reports"):
        self.reports_root = reports_root
        os.makedirs(self.reports_root, exist_ok=True)

    def generate_report_package(
        self,
        task_name: str,
        asset_or_query: str,
        title: str,
        summary: str,
        verification: Dict[str, Any],
        key_metrics: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        assumptions: List[str],
        limitations: List[str],
        facts: List[str],
        interpretations: List[str],
        uncertainties: List[str],
        catalysts: List[str],
        chart_paths: List[str]
    ) -> str:
        """Packages institutional research run into a timestamped directory."""
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H%M%S")
        safe_task = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in task_name)[:30].strip("_")
        run_dir_name = f"{timestamp_str}_{safe_task}"
        run_dir = os.path.join(self.reports_root, run_dir_name)
        charts_dir = os.path.join(run_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        # Copy/move chart images into charts_dir
        rel_chart_names = []
        for cp in chart_paths:
            if os.path.exists(cp):
                fname = os.path.basename(cp)
                target = os.path.join(charts_dir, fname)
                if os.path.abspath(cp) != os.path.abspath(target):
                    with open(cp, "rb") as src_f, open(target, "wb") as dst_f:
                        dst_f.write(src_f.read())
                rel_chart_names.append(target)

        # 1. Generate sources.csv
        sources_csv_path = os.path.join(run_dir, "sources.csv")
        with open(sources_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "url", "freshness", "observation_date", "retrieval_time_utc", "notes"])
            for s in sources:
                writer.writerow([
                    s.get("name", "Unknown"),
                    s.get("endpoint_url", s.get("url", "-")),
                    s.get("freshness", "DELAYED"),
                    s.get("observation_date", "-"),
                    s.get("retrieval_time_utc", "-"),
                    s.get("disclaimer", s.get("notes", "-"))
                ])

        # 2. Generate assumptions.md
        assumptions_md_path = os.path.join(run_dir, "assumptions.md")
        assumptions_text = f"""# Metodologi & Kerangka Asumsi Riset
Task: {task_name} | Tanggal: {now.strftime('%Y-%m-%d %H:%M:%S')}

## Asumsi Eksplisit
{chr(10).join(f"- {a}" for a in assumptions)}

## Keterbatasan & Batas Data (Data Limitations)
{chr(10).join(f"- {l}" for l in limitations)}

## Klasifikasi Bukti Epistemik
### Fakta Numerik / Dokumen Terverifikasi (Facts)
{chr(10).join(f"- {f}" for f in facts)}

### Interpretasi & Hipotesis Analitis (Interpretations)
{chr(10).join(f"- {i}" for i in interpretations)}

### Ketidakpastian & Risiko Pembatal Tesis (Uncertainties)
{chr(10).join(f"- {u}" for u in uncertainties)}
"""
        with open(assumptions_md_path, "w", encoding="utf-8") as f:
            f.write(assumptions_text)

        # 3. Generate summary.json
        summary_json_path = os.path.join(run_dir, "summary.json")
        summary_payload = {
            "title": title,
            "task_name": task_name,
            "asset": asset_or_query,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_level": verification.get("confidence_level", "Sedang"),
            "verdict": verification.get("verdict", "LULUS DENGAN CATATAN"),
            "key_metrics": key_metrics,
            "scenarios_count": len(scenarios),
            "sources_count": len(sources),
            "charts_count": len(rel_chart_names)
        }
        with open(summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2)

        # 4. Generate report.md
        report_md_path = os.path.join(run_dir, "report.md")
        metrics_table_rows = []
        for k, v in key_metrics.items():
            k_clean = k.replace("_", " ").title()
            val_str = f"{v:.2f}" if isinstance(v, float) else str(v)
            metrics_table_rows.append(f"| **{k_clean}** | {val_str} |")
        metrics_table = "\n".join(metrics_table_rows)

        scenario_rows = []
        for sc in scenarios:
            chg = sc.get("projected_change_pct", 0)
            scenario_rows.append(f"| **{sc.get('scenario')}** | {chg:+.2f}% | ${sc.get('projected_price', 0):.2f} | {sc.get('mechanism', '')} |")
        scenario_table = "\n".join(scenario_rows)

        catalysts_list = "\n".join(f"- {c}" for c in catalysts)

        report_md_content = f"""# {title}

**Target / Aset**: `{asset_or_query}`  
**Waktu Analisis**: `{now.strftime('%Y-%m-%d %H:%M:%S')} UTC`  
**Status Audit Skeptic / Verification**: `{verification.get('verdict', 'LULUS VERIFIKASI')}`  
**Tingkat Keyakinan**: **{verification.get('confidence_level', 'Sedang')}** ({verification.get('confidence_reason', '-')})

---

## 1. Executive Summary
{summary}

---

## 2. Metrik Kuantitatif & Fundamental Utama
| Metrik | Nilai Terhitung |
| :--- | :--- |
{metrics_table}

---

## 3. Analisis Skenario & Stress Testing (Bull / Base / Bear)
| Skenario Shock | Proyeksi Dampak (%) | Estimasi Harga | Mekanisme Transmisi |
| :--- | :--- | :--- | :--- |
{scenario_table}

---

## 4. Bukti & Validasi Tesis
### Fakta Terverifikasi (Facts)
{chr(10).join(f"- [Fakta] {f}" for f in facts)}

### Interpretasi Analitis (Interpretations)
{chr(10).join(f"- [Interpretasi] {i}" for i in interpretations)}

### Ketidakpastian & Titik Kegagalan (Uncertainties)
{chr(10).join(f"- [Ketidakpastian] {u}" for u in uncertainties)}

---

## 5. Katalis & Indikator Pantauan
{catalysts_list}

---

## 6. Asumsi & Keterbatasan Metodologi
- **Asumsi**:
{chr(10).join(f"  - {a}" for a in assumptions)}
- **Keterbatasan**:
{chr(10).join(f"  - {l}" for l in limitations)}

---

## 7. Sumber Data & Atribusi
| Sumber | Endpoint / URL | Status Kesegaran | Tanggal Observasi |
| :--- | :--- | :--- | :--- |
{chr(10).join(f"| {s.get('name', 'Source')} | {s.get('endpoint_url', s.get('url', '-'))} | {s.get('freshness', 'DELAYED')} | {s.get('observation_date', '-')} |" for s in sources)}

---

> [!NOTE]
> **Pernyataan Kepatuhan Institusional**: Laporan riset ini disusun secara otomatis oleh **AXIOM AI AGENTS** sebagai pendukung riset kuantitatif dan edukasi finansial. AXIOM bukan penasihat investasi terdaftar, tidak melakukan transaksi riil, dan tidak menyajikan anjuran beli/jual instrumen keuangan. Keputusan alokasi risiko sepenuhnya tanggung jawab pengguna.
"""
        with open(report_md_path, "w", encoding="utf-8") as f:
            f.write(report_md_content)

        # 5. Generate report.html
        report_html_path = os.path.join(run_dir, "report.html")
        HTMLReportGenerator.generate(
            title=title,
            asset_or_task=asset_or_query,
            summary=summary,
            confidence_level=verification.get("confidence_level", "Sedang"),
            confidence_reason=verification.get("confidence_reason", ""),
            key_metrics=key_metrics,
            scenarios=scenarios,
            sources=sources,
            assumptions=assumptions,
            limitations=limitations,
            charts=rel_chart_names,
            output_filepath=report_html_path
        )

        return run_dir
