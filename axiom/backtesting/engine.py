"""Backtesting Engine with strict timing alignment to eliminate look-ahead bias."""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from axiom.data.schemas import PriceBar
from axiom.backtesting.strategies import BaseStrategy, BuyAndHoldStrategy
from axiom.backtesting.metrics import BacktestMetrics

@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    period_start: str
    period_end: str
    equity_curve: pd.Series
    benchmark_curve: pd.Series
    metrics: Dict[str, Any]
    daily_positions: pd.Series
    trade_count: int
    annual_turnover: float
    total_transaction_costs: float

class BacktestEngine:
    def __init__(
        self,
        fee_rate: float = 0.0010, # 10 bps
        slippage_rate: float = 0.0005, # 5 bps
        rf_rate: float = 0.045
    ):
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
        self.rf_rate = rf_rate

    def run(
        self,
        bars: List[PriceBar],
        strategy: BaseStrategy,
        benchmark_bars: Optional[List[PriceBar]] = None,
        strategy_name: str = "Strategy"
    ) -> BacktestResult:
        if len(bars) < 20:
            raise ValueError("Bar harga tidak mencukupi untuk simulasi backtest (min 20 bar).")

        df = pd.DataFrame([b.model_dump() for b in bars])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")

        # Step 1: Generate Raw Signal at date t
        raw_signals = strategy.generate_signals(df)

        # Step 2: STRICT TIMING ALIGNMENT (PREVENT LOOK-AHEAD BIAS)
        # Position taken on day t is based on signal available at close of day t-1
        # Execution occurs at start of day t
        positions = raw_signals.shift(1).fillna(0.0)

        # Step 3: Turnover & Frictional Costs
        # Turnover occurs when position changes from previous day
        position_change = positions.diff().abs().fillna(positions.iloc[0])
        trade_count = int((position_change > 0).sum())

        frictional_cost_per_trade = self.fee_rate + self.slippage_rate
        cost_series = position_change * frictional_cost_per_trade
        total_costs = float(cost_series.sum())

        # Step 4: Net Daily Returns
        daily_returns = df["close"].pct_change().fillna(0.0)
        strategy_gross_returns = positions * daily_returns
        strategy_net_returns = strategy_gross_returns - cost_series

        # Step 5: Equity Curve ($1 initial base)
        equity_curve = (1.0 + strategy_net_returns).cumprod()

        # Step 6: Benchmark Curve
        benchmark_curve = (1.0 + daily_returns).cumprod()
        if benchmark_bars and len(benchmark_bars) >= len(bars):
            df_b = pd.DataFrame([b.model_dump() for b in benchmark_bars])
            df_b["date"] = pd.to_datetime(df_b["date"])
            df_b = df_b.sort_values("date").set_index("date")
            aligned_b = df_b.reindex(df.index).ffill().bfill()
            b_ret = aligned_b["close"].pct_change().fillna(0.0)
            benchmark_curve = (1.0 + b_ret).cumprod()

        # Step 7: Annual Turnover
        n_years = max(len(df) / 252.0, 0.05)
        annual_turnover = float(position_change.sum() / (2.0 * n_years))

        # Step 8: Performance Metrics
        metrics = BacktestMetrics.calculate(
            equity_curve=equity_curve,
            benchmark_curve=benchmark_curve,
            rf_rate=self.rf_rate,
            turnover=annual_turnover,
            total_costs=total_costs
        )

        return BacktestResult(
            strategy_name=strategy_name,
            symbol=bars[0].date if bars else "ASSET",
            period_start=df.index[0].strftime("%Y-%m-%d"),
            period_end=df.index[-1].strftime("%Y-%m-%d"),
            equity_curve=equity_curve,
            benchmark_curve=benchmark_curve,
            metrics=metrics,
            daily_positions=positions,
            trade_count=trade_count,
            annual_turnover=annual_turnover,
            total_transaction_costs=total_costs
        )
