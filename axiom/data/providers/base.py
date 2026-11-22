"""Base Data Provider interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from axiom.data.schemas import HistoricalData, FundamentalMetrics, MacroData, NewsArticle

class BaseDataProvider(ABC):
    @abstractmethod
    def get_historical_prices(self, symbol: str, period: str = "1y", interval: str = "1d") -> HistoricalData:
        pass

    @abstractmethod
    def get_fundamentals(self, symbol: str) -> FundamentalMetrics:
        pass

    @abstractmethod
    def get_macro(self, region: str = "US") -> MacroData:
        pass

    @abstractmethod
    def get_news(self, query: str, limit: int = 10) -> List[NewsArticle]:
        pass
