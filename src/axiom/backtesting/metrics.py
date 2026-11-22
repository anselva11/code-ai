"""Performance metrics calculation for backtest simulations."""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

class BacktestMetrics:
    @staticmethod
    def calculate(equity_curve: pd.Series, benchmark_curve: Optional[pd.Series] = None, rf_rate: float = 0.045, turnover: float = 0.0, total_costs: float = 0.0) -> Dict[str, Any]:
        """Computes institutional backtest performance metrics from an equity curve."""
        returns = equity_curve.pct_change().dropna()
        n_days = len(returns)
        if n_days < 2:
            return {"error": "Kurva ekuitas tidak mencukupi untuk evaluasi metrik."}

        n_years = max(n_days / 252.0, 0.05)
        start_val = equity_curve.iloc[0]
        end_val = equity_curve.iloc[-1]

        total_return = (end_val / start_val) - 1.0
        cagr = ((end_val / start_val) ** (1.0 / n_years)) - 1.0 if start_val > 0 else 0.0
        ann_vol = float(returns.std() * np.sqrt(252))

        # Sharpe
        excess_daily_rf = rf_rate / 252.0
        excess_returns = returns - excess_daily_rf
        sharpe = float(np.sqrt(252) * excess_returns.mean() / (returns.std() + 1e-9))

        # Sortino
        downside = returns[returns < 0]
        downside_std = float(downside.std() * np.sqrt(252)) if not downside.empty else 1e-9
        sortino = float((cagr - rf_rate) / downside_std)

        # Max Drawdown
        cummax = equity_curve.cummax()
        drawdown_series = (equity_curve - cummax) / cummax
        max_dd = float(drawdown_series.min())
        calmar = float(cagr / abs(max_dd)) if abs(max_dd) > 1e-6 else 0.0

        # Win Rate & Profit Factor
        pos_ret = returns[returns > 0]
        neg_ret = returns[returns < 0]
        win_rate = float(len(pos_ret) / len(returns)) if len(returns) > 0 else 0.0
        profit_factor = float(pos_ret.sum() / abs(neg_ret.sum())) if abs(neg_ret.sum()) > 1e-9 else 1.0

        bench_metrics = {}
        if benchmark_curve is not None and not benchmark_curve.empty:
            bench_ret = benchmark_curve.pct_change().dropna()
            b_n_years = max(len(bench_ret) / 252.0, 0.05)
            b_cagr = ((benchmark_curve.iloc[-1] / benchmark_curve.iloc[0]) ** (1.0 / b_n_years)) - 1.0
            b_cummax = benchmark_curve.cummax()
            b_max_dd = float(((benchmark_curve - b_cummax) / b_cummax).min())
            b_vol = float(bench_ret.std() * np.sqrt(252))
            b_sharpe = float(np.sqrt(252) * (bench_ret.mean() - excess_daily_rf) / (bench_ret.std() + 1e-9))

            bench_metrics = {
                "benchmark_cagr_pct": round(b_cagr * 100, 2),
                "benchmark_volatility_pct": round(b_vol * 100, 2),
                "benchmark_sharpe": round(b_sharpe, 2),
                "benchmark_max_drawdown_pct": round(b_max_dd * 100, 2),
                "alpha_cagr_pct": round((cagr - b_cagr) * 100, 2)
            }

        res = {
            "cagr_pct": round(cagr * 100, 2),
            "total_return_pct": round(total_return * 100, 2),
            "annualized_volatility_pct": round(ann_vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "calmar_ratio": round(calmar, 2),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "win_rate_pct": round(win_rate * 100, 2),
            "profit_factor": round(profit_factor, 2),
            "annual_turnover_pct": round(turnover * 100, 2),
            "total_frictional_costs_pct": round(total_costs * 100, 2),
            "observations_days": n_days
        }
        res.update(bench_metrics)
        return res
