"""Technical analysis engine: MAs, RSI, MACD, volatility, and drawdown."""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from axiom.data.schemas import PriceBar

class TechnicalAnalysis:
    @staticmethod
    def analyze(bars: List[PriceBar]) -> Dict[str, Any]:
        if not bars or len(bars) < 20:
            return {"error": "Observasi tidak mencukupi untuk analisa teknikal (minimal 20 bar)."}

        df = pd.DataFrame([b.model_dump() for b in bars])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        closes = df["close"]

        # Daily Returns & Volatility
        returns = closes.pct_change().dropna()
        realized_vol = float(returns.std() * np.sqrt(252)) if len(returns) > 1 else 0.0

        # Drawdown
        cummax = closes.cummax()
        drawdowns = (closes - cummax) / cummax
        max_drawdown = float(drawdowns.min())
        current_drawdown = float(drawdowns.iloc[-1])

        # Moving Averages
        sma_20 = float(closes.rolling(window=20).mean().iloc[-1]) if len(closes) >= 20 else None
        sma_50 = float(closes.rolling(window=50).mean().iloc[-1]) if len(closes) >= 50 else None
        sma_200 = float(closes.rolling(window=200).mean().iloc[-1]) if len(closes) >= 200 else None
        ema_20 = float(closes.ewm(span=20, adjust=False).mean().iloc[-1]) if len(closes) >= 20 else None

        # RSI (14)
        delta = closes.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_14 = float(rsi_series.dropna().iloc[-1]) if not rsi_series.dropna().empty else None

        # MACD (12, 26, 9)
        ema_12 = closes.ewm(span=12, adjust=False).mean()
        ema_26 = closes.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        curr_price = float(closes.iloc[-1])
        high_52w = float(closes.iloc[-252:].max()) if len(closes) >= 252 else float(closes.max())
        low_52w = float(closes.iloc[-252:].min()) if len(closes) >= 252 else float(closes.min())

        trend = "BULLISH" if sma_50 and sma_200 and sma_50 > sma_200 else "BEARISH"
        if sma_50 and curr_price < sma_50 and trend == "BULLISH":
            trend = "NEUTRAL / PULLBACK"

        return {
            "current_price": curr_price,
            "period_change_pct": float((curr_price / closes.iloc[0]) - 1.0),
            "high_52w": high_52w,
            "low_52w": low_52w,
            "realized_volatility_annualized": realized_vol,
            "max_drawdown": max_drawdown,
            "current_drawdown": current_drawdown,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "ema_20": ema_20,
            "rsi_14": rsi_14,
            "macd": float(macd_line.iloc[-1]),
            "macd_signal": float(signal_line.iloc[-1]),
            "macd_hist": float(macd_hist.iloc[-1]),
            "trend_regime": trend,
            "total_bars": len(df)
        }
