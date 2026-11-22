"""Mock Backend Implementation for AXIOM TUI.
Simulates a complete, realistic quantitative research lifecycle without requiring an external API key:
1. Stage: Rencana -> emits PlanReady, waits for approval
2. Stage: Analisa -> emits 3 realistic tool calls with syntax-highlighted code and outputs
3. Stage: Critic -> flags initial bias, auto-corrects, emits VerdictReady (LULUS DENGAN CATATAN)
4. Stage: Laporan -> emits ReportReady with structured markdown and metric tables
5. Saves run artifacts to runs/ directory for inspection
"""
import os
import json
import time
import asyncio
from datetime import datetime
from typing import AsyncIterator, List, Dict, Any, Optional
from axiom.tui.events import (
    StageStarted, StageFinished, PlanReady, ToolCall, ToolResult,
    VerdictReady, ReportReady, RunFinished, ErrorEvent
)
from axiom.tui.backend import RunSummary, RunDetail, Event

class MockBackend:
    def __init__(self, runs_dir: str = "runs", delay_factor: float = 1.0):
        self.runs_dir = runs_dir
        self.delay_factor = delay_factor
        os.makedirs(self.runs_dir, exist_ok=True)
        self._plan_decision_event: asyncio.Event = asyncio.Event()
        self._approved: bool = True
        self._edited_question: Optional[str] = None
        self._cancelled: bool = False
        self._seed_sample_runs()

    async def _sleep(self, duration: float) -> None:
        if self.delay_factor > 0:
            await asyncio.sleep(duration * self.delay_factor)

    def _seed_sample_runs(self) -> None:
        """Seeds initial realistic runs if runs directory is empty."""
        run1_dir = os.path.join(self.runs_dir, "run_20261120_001")
        if not os.path.exists(run1_dir):
            os.makedirs(run1_dir, exist_ok=True)
            meta = {
                "id": "run_20261120_001",
                "timestamp": "2026-11-20 14:32:10",
                "verdict": "LULUS DENGAN CATATAN",
                "question": "Bandingkan momentum 12-1 bulan vs buy-and-hold di saham LQ45 5 tahun terakhir",
                "mode": "quant",
                "audience": "analis",
                "chart_files": ["momentum_cumulative_return.png"]
            }
            with open(os.path.join(run1_dir, "run_meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

            plan = [
                {"step": "1", "agent": "Data Agent", "task": "Ingestion data penutupan LQ45 point-in-time", "success_criteria": "Missing values 0%"},
                {"step": "2", "agent": "Quant Agent", "task": "Kalkulasi faktor momentum 12-1m dan quantile returns", "success_criteria": "Deterministik Sharpe & p-value"},
                {"step": "3", "agent": "Critic Agent", "task": "Audit look-ahead bias pada tanggal rebalancing", "success_criteria": "Verifikasi audit lolos"},
                {"step": "4", "agent": "Report Agent", "task": "Penyusunan laporan komparatif & ringkasan risiko", "success_criteria": "Laporan terstruktur selesai"}
            ]
            with open(os.path.join(run1_dir, "plan.json"), "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2)

            tools = [
                {
                    "step": 1,
                    "agent": "Data Agent",
                    "code": "import duckdb\ncon = duckdb.connect()\nprices = con.execute(\"SELECT date, ticker, close FROM read_csv_auto('data/lq45.csv')\").df()\nprint(f'Loaded {len(prices)} rows across 45 tickers.')\nprint('Corporate actions: 100% split & dividend adjusted.')",
                    "output": "Loaded 1240 rows across 45 tickers.\nCorporate actions: 100% split & dividend adjusted.\nMissing data rate: 0.00%"
                },
                {
                    "step": 2,
                    "agent": "Quant Agent",
                    "code": "import numpy as np\ndef momentum_signal(prices):\n    ret_12m = prices.pct_change(252)\n    ret_1m = prices.pct_change(21)\n    return ret_12m - ret_1m\nprint('Sharpe Momentum: 1.42 (vs Benchmark: 0.88)')\nprint('Max Drawdown: -14.2% (vs Benchmark: -22.5%)')",
                    "output": "Sharpe Momentum: 1.42 (vs Benchmark: 0.88)\nMax Drawdown: -14.2% (vs Benchmark: -22.5%)\nT-stat: 2.34 (p-value: 0.0195)"
                }
            ]
            with open(os.path.join(run1_dir, "tool_calls.json"), "w", encoding="utf-8") as f:
                json.dump(tools, f, indent=2)

            critic = {
                "verdict": "LULUS DENGAN CATATAN",
                "findings": [
                    {"severity": "Sedang", "finding": "Rebalancing bulanan dialihkan ke harga open t+1 untuk mencegah look-ahead bias.", "mitigation": "Diterapkan pada engine backtest."},
                    {"severity": "Rendah", "finding": "Universe terbatas pada LQ45 yang bertahan, potensi survivorship bias dicegah oleh point-in-time table.", "mitigation": "Telah divalidasi dengan dataset point-in-time v1.2."}
                ]
            }
            with open(os.path.join(run1_dir, "critic.json"), "w", encoding="utf-8") as f:
                json.dump(critic, f, indent=2)

            report = """# Laporan Riset: Momentum 12-1 Bulan di Saham LQ45 (2020-2025)

## Ringkasan Eksekutif
Strategi momentum 12-1 bulan menunjukkan performa risk-adjusted yang lebih unggul dibandingkan indeks acuan IHSG pada periode 2020–2025.

| Metrik | Strategi Momentum 12-1M | Benchmark (LQ45 / IHSG) |
| :--- | :--- | :--- |
| **CAGR** | **18.4%** | 8.2% |
| **Annualized Volatility** | 13.8% | 16.1% |
| **Sharpe Ratio** | **1.42** | 0.88 |
| **Max Drawdown** | **-14.2%** | -22.5% |
| **Turnover Tahunan** | 185% | 0% |

### Temuan Verifikasi Critic
- **Status Verdict**: `LULUS DENGAN CATATAN`
- Data leakage & look-ahead bias: Negatif (Telah diaudit).
- Asumsi biaya transaksi: 0.15% fee beli, 0.25% fee jual, slippage 0.05%.

> [!NOTE]
> **Tingkat Keyakinan**: Sedang-Tinggi. Sinyal momentum terbukti secara statistik signifikan (p-value = 0.0195).
> **Keterbatasan**: Sensitif terhadap likuiditas saat periode pasar volatil ekstrem.
> **Disclaimer**: Hasil riset analitis AXIOM untuk analisis quant, bukan rekomendasi beli/jual instrumen keuangan.
"""
            with open(os.path.join(run1_dir, "report.md"), "w", encoding="utf-8") as f:
                f.write(report)

            # 1x1 dummy PNG
            with open(os.path.join(run1_dir, "momentum_cumulative_return.png"), "wb") as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

    async def run(self, question: str, mode: str = "quant", audience: str = "analis") -> AsyncIterator[Event]:
        self._cancelled = False
        self._plan_decision_event.clear()
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        active_question = question

        # Stage 1: Rencana
        yield StageStarted(stage="Rencana")
        await self._sleep(0.4)

        plan = [
            {
                "step": "1",
                "agent": "Data Agent",
                "task": f"Ingestion data universe LQ45 & penyesuaian corporate action untuk: {active_question[:40]}...",
                "success_criteria": "Missing values 0.00%, point-in-time bebas survivorship bias."
            },
            {
                "step": "2",
                "agent": "Quant Agent",
                "task": "Kalkulasi matriks kovarian, sinyal cross-sectional faktor, dan uji t-statistik.",
                "success_criteria": "Hasil deterministik dihitung via sandbox Python."
            },
            {
                "step": "3",
                "agent": "Backtest Agent",
                "task": "Simulasi walk-forward out-of-sample dengan estimasi biaya transaksi & slippage.",
                "success_criteria": "Sharpe, Sortino, Max Drawdown, dan Turnover tercatat."
            },
            {
                "step": "4",
                "agent": "Critic Agent",
                "task": "Audit data leakage, look-ahead bias, p-hacking, dan multiple testing correction.",
                "success_criteria": "Verifikasi ketat sebelum kesimpulan disajikan."
            },
            {
                "step": "5",
                "agent": "Report Agent",
                "task": f"Sintesis laporan eksekutif disesuaikan untuk audiens: {audience.upper()}.",
                "success_criteria": "Laporan terstruktur dengan asumsi & keterbatasan."
            }
        ]

        yield PlanReady(
            plan=plan,
            summary=f"Disiapkan rencana 5 langkah untuk mengevaluasi '{active_question}' dengan target audiens [{audience}]."
        )

        # Wait for user approval
        await self._plan_decision_event.wait()

        if self._cancelled or not self._approved:
            yield ErrorEvent(
                message="Eksekusi rencana dibatalkan oleh pengguna.",
                hint="Anda dapat mengedit pertanyaan atau mengubah parameter mode sebelum menjalankan kembali."
            )
            yield RunFinished(run_id=run_id, success=False)
            return

        if self._edited_question:
            active_question = self._edited_question

        yield StageFinished(stage="Rencana", duration=1.2)

        # Stage 2: Analisa
        yield StageStarted(stage="Analisa")
        await self._sleep(0.3)

        tool_calls_history = []

        # Tool Call 1: Data Agent
        t1_code = (
            "# Data Agent: Membaca dataset point-in-time\n"
            "import duckdb, pandas as pd\n"
            "con = duckdb.connect()\n"
            "query = \"\"\"\n"
            "SELECT ticker, date, close, split_factor, dividend\n"
            "FROM 'data/lq45_constituents_point_in_time.csv'\n"
            "WHERE date >= '2020-01-01'\n"
            "ORDER BY ticker, date\n"
            "\"\"\"\n"
            "print('Data quality audit: 0 missing dates, 100% split adjusted.')"
        )
        t1_output = (
            "Loaded 45 tickers (1,240 bursa days).\n"
            "Data Quality Audit: PASSED\n"
            "- Missing data rate: 0.00%\n"
            "- Survivorship bias filter: Point-in-time active"
        )
        tool_calls_history.append({"step": 1, "agent": "Data Agent", "code": t1_code, "output": t1_output})
        yield ToolCall(code=t1_code, step=1, agent="Data Agent")
        await self._sleep(0.6)
        yield ToolResult(output=t1_output, step=1, error=False)

        # Tool Call 2: Quant Agent
        t2_code = (
            "# Quant Agent: Perhitungan sinyal momentum 12-1m\n"
            "import numpy as np\n"
            "def calculate_momentum_12_1(df):\n"
            "    # Skip return 1 bulan terakhir untuk menghindari short-term reversal\n"
            "    r_12m = df['close'].pct_change(252)\n"
            "    r_1m = df['close'].pct_change(21)\n"
            "    signal = r_12m - r_1m\n"
            "    return signal.dropna()\n\n"
            "print('T-statistic: 2.38 | p-value: 0.0178 (Signifikan pada alpha 5%)')"
        )
        t2_output = (
            "Factor Metrics:\n"
            "- Mean Annual Spread (Q1 Top vs Q5 Bottom): +11.4%\n"
            "- T-statistic: 2.38\n"
            "- P-value: 0.0178 (Signifikan secara statistik)"
        )
        tool_calls_history.append({"step": 2, "agent": "Quant Agent", "code": t2_code, "output": t2_output})
        yield ToolCall(code=t2_code, step=2, agent="Quant Agent")
        await self._sleep(0.7)
        yield ToolResult(output=t2_output, step=2, error=False)

        # Tool Call 3: Backtest Agent
        t3_code = (
            "# Backtest Agent: Simulasi walk-forward dengan biaya transaksi\n"
            "costs = {'buy_fee': 0.0015, 'sell_fee': 0.0025, 'slippage': 0.0005}\n"
            "results = run_walk_forward(strategy='momentum_12_1', universe='LQ45', costs=costs)\n"
            "print(f'CAGR: {results.cagr:.1%}')\n"
            "print(f'Sharpe: {results.sharpe:.2f}')\n"
            "print(f'Max Drawdown: {results.max_dd:.1%}')"
        )
        t3_output = (
            "Simulation Results (2020-2025, Net of Fees):\n"
            "- CAGR: 18.4% (vs IHSG Benchmark 8.2%)\n"
            "- Annual Volatility: 13.8%\n"
            "- Sharpe Ratio: 1.42 (vs Benchmark 0.88)\n"
            "- Max Drawdown: -14.2% (vs Benchmark -22.5%)\n"
            "- Annual Turnover: 185%"
        )
        tool_calls_history.append({"step": 3, "agent": "Backtest Agent", "code": t3_code, "output": t3_output})
        yield ToolCall(code=t3_code, step=3, agent="Backtest Agent")
        await self._sleep(0.6)
        yield ToolResult(output=t3_output, step=3, error=False)

        yield StageFinished(stage="Analisa", duration=3.2)

        # Stage 3: Critic
        yield StageStarted(stage="Critic")
        await self._sleep(0.3)

        # Critic audit check 1 (Rejection/Flagging)
        c1_code = (
            "# Critic Agent: Audit look-ahead bias pada tanggal eksekusi rebalancing\n"
            "check_date_alignment(prices_date='close_t', trade_date='exec_t')"
        )
        c1_output = (
            "[PERINGATAN AUDIT]: Deteksi potensi Look-Ahead Bias.\n"
            "Rebalancing menggunakan sinyal harga close hari t untuk eksekusi di hari t yang sama.\n"
            "-> Tindakan Perbaikan: Menggeser eksekusi ke harga open t+1."
        )
        tool_calls_history.append({"step": 4, "agent": "Critic Agent", "code": c1_code, "output": c1_output})
        yield ToolCall(code=c1_code, step=4, agent="Critic Agent")
        await self._sleep(0.6)
        yield ToolResult(output=c1_output, step=4, error=True)

        # Critic audit check 2 (Re-audit after correction)
        c2_code = (
            "# Critic Agent: Verifikasi ulang setelah penyesuaian eksekusi open t+1\n"
            "verify_corrected_pipeline(trade_date='open_t_plus_1', multiple_tests_count=4)"
        )
        c2_output = (
            "[VERIFIKASI LOLOS DENGAN CATATAN]:\n"
            "- Look-ahead bias: Diatasi (Sharpe disesuaikan dari 1.48 -> 1.42).\n"
            "- Data leakage: 0%\n"
            "- Koreksi Multiple Testing: Holm-Bonferroni p-adjusted = 0.038 (tetap signifikan)."
        )
        tool_calls_history.append({"step": 5, "agent": "Critic Agent", "code": c2_code, "output": c2_output})
        yield ToolCall(code=c2_code, step=5, agent="Critic Agent")
        await self._sleep(0.6)
        yield ToolResult(output=c2_output, step=5, error=False)

        findings = [
            {
                "severity": "Sedang",
                "finding": "Eksekusi simulasi dialihkan ke harga open t+1 untuk mencegah bias antisipasi harga penutupan.",
                "mitigation": "Sharpe disesuaikan konservatif dari 1.48 menjadi 1.42."
            },
            {
                "severity": "Rendah",
                "finding": "Turnover tahunan 185% membebankan biaya friksi trading pada saham berkapitalisasi menengah.",
                "mitigation": "Dibatasi pada konstituen likuiditas tinggi indeks LQ45."
            }
        ]
        yield VerdictReady(verdict="LULUS DENGAN CATATAN", findings=findings)
        yield StageFinished(stage="Critic", duration=2.1)

        # Stage 4: Laporan
        yield StageStarted(stage="Laporan")
        await self._sleep(0.4)

        report_markdown = f"""# Laporan Riset Kuantitatif AXIOM

### Pertanyaan Riset
> **"{active_question}"**

---

### Metrik Kinerja Portofolio (Net of Fees: 2020 – 2025)

| Metrik Kuantitatif | Strategi Momentum 12-1M | Benchmark (LQ45 / IHSG) | Selisih / Alpha |
| :--- | :--- | :--- | :--- |
| **CAGR (Pertumbuhan Tahunan)** | **18.4%** | 8.2% | **+10.2%** |
| **Annualized Volatility** | 13.8% | 16.1% | -2.3% |
| **Sharpe Ratio** (Rf = 5.5%) | **1.42** | 0.88 | **+0.54** |
| **Sortino Ratio** | **1.96** | 1.12 | **+0.84** |
| **Maximum Drawdown (MDD)** | **-14.2%** | -22.5% | **+8.3% (Lebih Tangguh)** |
| **Annual Turnover** | 185% | 0.0% | +185% |
| **T-Statistic (Spread Return)** | **2.38** (p = 0.0178) | - | Signifikan pada α = 5% |

---

### Temuan Audit Critic
- **Status Verdict**: `[!] LULUS DENGAN CATATAN`
- **Audit Bias**: Skenario eksekusi awal yang rentan look-ahead bias telah dikoreksi ke harga open hari bursa berikutnya (t+1).
- **Multiple Testing**: Dicatat 4 variasi parameter; setelah penyesuaian Holm-Bonferroni, p-value tetap berada di bawah ambang batas signifikansi 0.05.

---

### Asumsi & Keterbatasan Metodologi
1. **Asumsi Biaya**: Fee beli 0.15%, fee jual 0.25%, slippage estimasi 0.05% per transaksi.
2. **Keterbatasan Likuiditas**: Kapasitas strategi diproyeksikan optimal hingga dana kelolaan Rp 50 Miliar tanpa memicu impak harga (market impact) berlebih.
3. **Tingkat Keyakinan**: **Tinggi** (Kalkulasi deterministik via sandbox Python, lolos audit Critic, dataset point-in-time bebas survivorship bias).

> **Pernyataan Kepatuhan**: Dokumen ini disusun oleh AXIOM sebagai perangkat riset kuantitatif objektif. Dokumen ini bukan merupakan anjuran, tawaran, atau nasihat untuk membeli atau menjual efek apa pun. Keputusan investasi sepenuhnya berada di tangan pengguna.
"""
        yield ReportReady(markdown=report_markdown)

        # Save run to disk
        run_folder = os.path.join(self.runs_dir, run_id)
        os.makedirs(run_folder, exist_ok=True)
        meta = {
            "id": run_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "verdict": "LULUS DENGAN CATATAN",
            "question": active_question,
            "mode": mode,
            "audience": audience,
            "chart_files": []
        }
        with open(os.path.join(run_folder, "run_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        with open(os.path.join(run_folder, "plan.json"), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        with open(os.path.join(run_folder, "tool_calls.json"), "w", encoding="utf-8") as f:
            json.dump(tool_calls_history, f, indent=2)
        with open(os.path.join(run_folder, "critic.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "LULUS DENGAN CATATAN", "findings": findings}, f, indent=2)
        with open(os.path.join(run_folder, "report.md"), "w", encoding="utf-8") as f:
            f.write(report_markdown)

        yield StageFinished(stage="Laporan", duration=1.0)
        yield RunFinished(run_id=run_id, success=True)

    def approve_plan(self, approved: bool, edited_question: Optional[str] = None) -> None:
        self._approved = approved
        self._edited_question = edited_question
        self._plan_decision_event.set()

    def cancel(self) -> None:
        self._cancelled = True
        self._plan_decision_event.set()

    def list_runs(self) -> List[RunSummary]:
        runs = []
        if not os.path.exists(self.runs_dir):
            return runs
        for entry in sorted(os.listdir(self.runs_dir), reverse=True):
            entry_path = os.path.join(self.runs_dir, entry)
            meta_path = os.path.join(entry_path, "run_meta.json")
            if os.path.isdir(entry_path) and os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        runs.append(RunSummary(
                            id=data.get("id", entry),
                            timestamp=data.get("timestamp", ""),
                            verdict=data.get("verdict", "BELUM VERIFIKASI"),
                            question=data.get("question", ""),
                            mode=data.get("mode", "quant"),
                            audience=data.get("audience", "analis")
                        ))
                except Exception:
                    continue
        return runs

    def load_run(self, run_id: str) -> RunDetail:
        run_folder = os.path.join(self.runs_dir, run_id)
        if not os.path.exists(run_folder):
            raise FileNotFoundError(f"Run {run_id} tidak ditemukan.")

        def load_json(name: str, default: Any) -> Any:
            p = os.path.join(run_folder, name)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default

        meta = load_json("run_meta.json", {})
        plan = load_json("plan.json", [])
        tool_calls = load_json("tool_calls.json", [])
        critic = load_json("critic.json", {})

        report_md = ""
        report_path = os.path.join(run_folder, "report.md")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report_md = f.read()

        chart_files = [f for f in os.listdir(run_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        return RunDetail(
            id=run_id,
            question=meta.get("question", ""),
            mode=meta.get("mode", "quant"),
            audience=meta.get("audience", "analis"),
            verdict=critic.get("verdict", meta.get("verdict", "BELUM VERIFIKASI")),
            plan=plan,
            tool_calls=tool_calls,
            critic_findings=critic.get("findings", []),
            report_markdown=report_md,
            chart_files=chart_files
        )
