"""Standardized rule-based quantitative strategies."""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Returns binary or weighted signal series (e.g. 1.0 for Long, 0.0 for Cash)."""
        pass

class MomentumStrategy(BaseStrategy):
    """12-1 Month Time-Series Momentum strategy (skips recent 1 month to avoid short-term reversal)."""
    def __init__(self, lookback_days: int = 252, skip_days: int = 21):
        self.lookback_days = lookback_days
        self.skip_days = skip_days

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        closes = df["close"]
        ret_lookback = closes.pct_change(self.lookback_days)
        ret_skip = closes.pct_change(self.skip_days)
        momentum = ret_lookback - ret_skip
        # Signal 1 when momentum > 0, else 0
        signals = (momentum > 0).astype(float)
        return signals

class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover trend-following strategy (e.g. 50/200 SMA)."""
    def __init__(self, fast_window: int = 50, slow_window: int = 200):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        closes = df["close"]
        sma_fast = closes.rolling(window=self.fast_window).mean()
        sma_slow = closes.rolling(window=self.slow_window).mean()
        signals = (sma_fast > sma_slow).astype(float)
        return signals

class MeanReversionStrategy(BaseStrategy):
    """RSI-based Mean Reversion strategy."""
    def __init__(self, rsi_period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        closes = df["close"]
        delta = closes.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        signals = pd.Series(0.0, index=df.index)
        signals[rsi < self.oversold] = 1.0 # Buy dip
        signals[rsi > self.overbought] = 0.0 # Exit
        return signals.ffill().fillna(0.0)

class BuyAndHoldStrategy(BaseStrategy):
    """Always invested benchmark strategy."""
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(1.0, index=df.index)
