"""Market Data Agent: Ingestion, validation, freshness check, and normalization."""
from typing import Dict, Any, List, Optional
from axiom.data.providers.yahoo import YahooFinanceProvider
from axiom.data.validation import DataValidator
from axiom.data.schemas import HistoricalData

class MarketDataAgent:
    def __init__(self, provider: Optional[YahooFinanceProvider] = None):
        self.provider = provider or YahooFinanceProvider()

    def fetch_market_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """Fetches historical market data, runs hygiene validation, and assesses freshness."""
        raw_data: HistoricalData = self.provider.get_historical_prices(symbol, period=period, interval=interval)
        is_valid, issues = DataValidator.validate_price_bars(raw_data.bars)

        latest_bar = raw_data.bars[-1] if raw_data.bars else None
        prev_bar = raw_data.bars[-2] if len(raw_data.bars) >= 2 else latest_bar

        change_pct = 0.0
        if latest_bar and prev_bar and prev_bar.close > 0:
            change_pct = ((latest_bar.close / prev_bar.close) - 1.0) * 100.0

        return {
            "symbol": raw_data.symbol,
            "asset_type": raw_data.asset_type,
            "currency": raw_data.currency,
            "total_bars": len(raw_data.bars),
            "latest_close": latest_bar.close if latest_bar else 0.0,
            "latest_date": latest_bar.date if latest_bar else "",
            "latest_change_pct": round(change_pct, 2),
            "latest_volume": latest_bar.volume if latest_bar else 0.0,
            "validation_passed": is_valid,
            "validation_issues": issues,
            "source": raw_data.source.model_dump(),
            "bars": raw_data.bars
        }
