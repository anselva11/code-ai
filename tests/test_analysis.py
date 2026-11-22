"""Unit tests for analytical engines: technical, fundamental, quant, and risk."""
import pytest
import pandas as pd
import numpy as np
from axiom.data.schemas import PriceBar, FundamentalMetrics, SourceRecord, FreshnessStatus
from axiom.analysis.technical import TechnicalAnalysis
from axiom.analysis.fundamental import FundamentalAnalysis
from axiom.analysis.quant import QuantAnalysis
from axiom.analysis.risk import RiskAnalysis

@pytest.fixture
def sample_bars():
    bars = []
    # 60 days of sinusoidal trend
    for i in range(60):
        price = 100.0 + 10.0 * np.sin(i / 10.0) + (i * 0.2)
        bars.append(PriceBar(
            date=f"2025-01-{(i % 28)+1:02d}",
            open=price,
            high=price + 1.0,
            low=price - 1.0,
            close=price,
            volume=50000.0
        ))
    return bars

def test_technical_analysis(sample_bars):
    res = TechnicalAnalysis.analyze(sample_bars)
    assert "error" not in res
    assert "current_price" in res
    assert "realized_volatility_annualized" in res
    assert res["realized_volatility_annualized"] > 0
    assert "rsi_14" in res
    assert 0 <= res["rsi_14"] <= 100
    assert "trend_regime" in res

def test_quant_analysis(sample_bars):
    metrics = QuantAnalysis.calculate_metrics(sample_bars, rf_rate=0.045)
    assert "cagr_pct" in metrics
    assert "sharpe_ratio" in metrics
    assert "sortino_ratio" in metrics
    assert "max_drawdown_pct" in metrics
    assert metrics["max_drawdown_pct"] <= 0.0

def test_risk_analysis(sample_bars):
    res = RiskAnalysis.calculate_var_cvar(sample_bars)
    assert "var_95_1d_pct" in res
    assert "cvar_95_1d_pct" in res
    assert res["cvar_95_1d_pct"] >= res["var_95_1d_pct"] # Expected Shortfall is at least as severe as VaR

def test_fundamental_analysis():
    source = SourceRecord(
        name="Test",
        endpoint_url="https://test.com",
        retrieval_time_utc="2026-01-01T00:00:00Z",
        observation_date="2026-01-01",
        asset="AAPL",
        freshness=FreshnessStatus.END_OF_DAY
    )
    fund = FundamentalMetrics(
        symbol="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=3000000000000.0,
        trailing_pe=28.5,
        forward_pe=25.0,
        price_to_sales=7.5,
        price_to_book=40.0,
        revenue_growth=0.08,
        gross_margin=0.45,
        net_margin=0.25,
        roe=1.5,
        free_cash_flow=100000000000.0,
        debt_to_equity=120.0,
        dividend_yield=0.005,
        source=source
    )
    eval_res = FundamentalAnalysis.evaluate(fund)
    assert eval_res["symbol"] == "AAPL"
    assert "Valuasi" in eval_res["valuation_summary"]
    assert eval_res["net_margin_pct"] == 25.0
