"""Quantitative statistics, risk-adjusted ratios, and benchmark comparisons."""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
from axiom.data.schemas import PriceBar

class QuantAnalysis:
    @staticmethod
    def calculate_metrics(bars: List[PriceBar], rf_rate: float = 0.045) -> Dict[str, Any]:
        """Calculates institutional quantitative metrics from historical price bars."""
        if not bars or len(bars) < 10:
            return {"error": "Observasi tidak cukup untuk metrik kuantitatif."}

        df = pd.DataFrame([b.model_dump() for b in bars])
        closes = df["close"]
        returns = closes.pct_change().dropna()
        n_days = len(returns)

        # Annualized Return & CAGR
        total_ret = (closes.iloc[-1] / closes.iloc[0]) - 1.0
        n_years = max(n_days / 252.0, 0.05)
        cagr = ((closes.iloc[-1] / closes.iloc[0]) ** (1.0 / n_years)) - 1.0 if closes.iloc[0] > 0 else 0.0

        # Volatility
        ann_vol = float(returns.std() * np.sqrt(252))

        # Sharpe Ratio
        excess_daily_rf = rf_rate / 252.0
        excess_returns = returns - excess_daily_rf
        sharpe = float(np.sqrt(252) * excess_returns.mean() / (returns.std() + 1e-9))

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = float(downside_returns.std() * np.sqrt(252)) if not downside_returns.empty else 1e-9
        sortino = float((cagr - rf_rate) / (downside_std + 1e-9))

        # Max Drawdown & Calmar
        cummax = closes.cummax()
        drawdowns = (closes - cummax) / cummax
        max_dd = float(drawdowns.min())
        calmar = float(cagr / abs(max_dd)) if abs(max_dd) > 1e-6 else 0.0

        # Distribution shape
        skewness = float(stats.skew(returns)) if len(returns) > 2 else 0.0
        kurtosis = float(stats.kurtosis(returns)) if len(returns) > 3 else 0.0

        # Win Rate
        pos_days = (returns > 0).sum()
        win_rate = float(pos_days / n_days) if n_days > 0 else 0.0

        return {
            "total_return_pct": float(total_ret * 100),
            "cagr_pct": float(cagr * 100),
            "annualized_volatility_pct": float(ann_vol * 100),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "calmar_ratio": round(calmar, 2),
            "max_drawdown_pct": float(max_dd * 100),
            "skewness": round(skewness, 2),
            "kurtosis": round(kurtosis, 2),
            "daily_win_rate_pct": float(win_rate * 100),
            "risk_free_rate_assumed": rf_rate,
            "observations_count": n_days
        }

    @staticmethod
    def compare_benchmark(asset_bars: List[PriceBar], bench_bars: List[PriceBar]) -> Dict[str, Any]:
        """Calculates Beta, Correlation, and Alpha against benchmark."""
        df_a = pd.DataFrame([b.model_dump() for b in asset_bars]).set_index("date")["close"]
        df_b = pd.DataFrame([b.model_dump() for b in bench_bars]).set_index("date")["close"]

        combined = pd.concat([df_a, df_b], axis=1, keys=["asset", "bench"]).dropna()
        if len(combined) < 15:
            return {"correlation": 0.0, "beta": 1.0}

        ret = combined.pct_change().dropna()
        corr = float(ret["asset"].corr(ret["bench"]))
        cov = ret["asset"].cov(ret["bench"])
        bench_var = ret["bench"].var()
        beta = float(cov / (bench_var + 1e-9))

        return {
            "correlation_with_benchmark": round(corr, 3),
            "beta_to_benchmark": round(beta, 2),
            "paired_observations": len(ret)
        }
