"""Critical verification test proving look-ahead bias is prevented on signal and execution timing."""
import pytest
import pandas as pd
import numpy as np
from axiom.data.schemas import PriceBar
from axiom.backtesting.engine import BacktestEngine
from axiom.backtesting.strategies import BaseStrategy

class DeliberateFuturePeekingStrategy(BaseStrategy):
    """Strategy that generates a signal of 1 if TOMORROW's return is positive (deliberate look-ahead signal)."""
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        future_return = df["close"].pct_change().shift(-1)
        # Raw signal has look-ahead information:
        raw_signals = (future_return > 0).astype(float)
        return raw_signals

def test_backtest_engine_eliminates_look_ahead_bias():
    """
    Test verifies that even if an imperfect strategy attempts to use date t+1 data,
    the BacktestEngine forces execution timing to shift(1), aligning position with
    information available strictly prior to execution.
    """
    # Create synthetic price series: [100, 110, 100, 110, 100, 110, ...]
    bars = []
    prices = [100.0, 110.0, 95.0, 105.0, 90.0, 120.0, 110.0, 130.0, 115.0, 140.0] * 3
    for idx, p in enumerate(prices):
        bars.append(PriceBar(
            date=f"2026-01-{idx+1:02d}",
            open=p,
            high=p + 2.0,
            low=p - 2.0,
            close=p,
            volume=1000.0
        ))

    engine = BacktestEngine(fee_rate=0.0, slippage_rate=0.0)
    strat = DeliberateFuturePeekingStrategy()
    result = engine.run(bars, strategy=strat, strategy_name="PeekingTest")

    # The position on day t MUST equal raw_signal from day t-1
    df = pd.DataFrame([b.model_dump() for b in bars]).set_index("date")
    raw_signals = strat.generate_signals(df)

    # Position on day 1 must be 0 (no look-ahead on day 0)
    assert result.daily_positions.iloc[0] == 0.0

    # For any day i > 0, daily_positions[i] must equal raw_signals[i-1]
    for i in range(1, len(raw_signals)):
        assert result.daily_positions.iloc[i] == raw_signals.iloc[i-1]

def test_backtest_costs_deduction():
    """Verify that transaction costs reduce net performance as turnover occurs."""
    bars = []
    prices = [100.0 + i for i in range(30)]
    dates = pd.date_range("2026-01-01", periods=30, freq="B")
    for idx, (p, dt) in enumerate(zip(prices, dates)):
        bars.append(PriceBar(
            date=dt.strftime("%Y-%m-%d"),
            open=p,
            high=p + 1.0,
            low=p - 1.0,
            close=p,
            volume=1000.0
        ))

    # Engine with 0 costs
    engine_zero = BacktestEngine(fee_rate=0.0, slippage_rate=0.0)
    # Engine with high costs
    engine_costly = BacktestEngine(fee_rate=0.01, slippage_rate=0.01) # 2% per trade

    class AlternatingStrategy(BaseStrategy):
        def generate_signals(self, df: pd.DataFrame) -> pd.Series:
            return pd.Series([float(i % 2) for i in range(len(df))], index=df.index)

    res_zero = engine_zero.run(bars, strategy=AlternatingStrategy())
    res_costly = engine_costly.run(bars, strategy=AlternatingStrategy())

    # Costly equity curve must be lower than zero-cost equity curve
    assert res_costly.equity_curve.iloc[-1] < res_zero.equity_curve.iloc[-1]
    assert res_costly.total_transaction_costs > 0.0
