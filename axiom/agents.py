"""Specialist Agents definition for AXIOM.
Layer 3 in the AXIOM architecture:
- Data Agent: Data ingestion, missing value checks, corporate action adjustment.
- Research Agent: Financial statements, 10-K/transcripts reading with citations.
- Quant Agent: Statistics, econometric factor calculation, t-stats, p-values.
- Risk Agent: VaR/CVaR, stress test, regime sensitivity.
- Backtest Agent: Walk-forward, slippage, turnover, MDD.
- Critic/Verifier Agent: Bias detection (look-ahead, survivorship, p-hacking, missing sources).
- Report Agent: Structured executive synthesis, narrative, and risk disclosures.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AgentRole:
    name: str
    description: str
    primary_tools: List[str]

AGENTS = {
    "Data": AgentRole(
        name="Data Agent",
        description="Ingestion, data hygiene, corporate action adjustments, quality audit.",
        primary_tools=["duckdb", "parquet_reader", "clean_missing"]
    ),
    "Research": AgentRole(
        name="Research Agent",
        description="Financial statements, XBRL, transcripts, extraction with exact citations.",
        primary_tools=["doc_parser", "vector_search", "citation_linker"]
    ),
    "Quant": AgentRole(
        name="Quant Agent",
        description="Statistical factor calculation, momentum, value, regression, hypothesis testing.",
        primary_tools=["statsmodels", "scipy_stats", "factor_calc"]
    ),
    "Risk": AgentRole(
        name="Risk Agent",
        description="VaR/CVaR, drawdown analysis, stress testing, macro sensitivity.",
        primary_tools=["var_calc", "stress_tester", "correlation_matrix"]
    ),
    "Backtest": AgentRole(
        name="Backtest Agent",
        description="Simulation with realistic costs, slippage, walk-forward out-of-sample.",
        primary_tools=["walk_forward_engine", "metrics_calc"]
    ),
    "Critic": AgentRole(
        name="Critic Agent",
        description="Mandatory verification: checks data leakage, look-ahead bias, p-hacking, claims without sources.",
        primary_tools=["leakage_scanner", "multiple_testing_adjuster", "source_verifier"]
    ),
    "Report": AgentRole(
        name="Report Agent",
        description="Synthesizes findings into audience-tailored reports with explicit assumptions & limitations.",
        primary_tools=["markdown_builder", "chart_styler", "export_pdf"]
    )
}
