"""Macro Agent: Yield curve, rates, inflation, commodities, and macroeconomic transmissions."""
from typing import Dict, Any, Optional, List
from axiom.data.providers.yahoo import YahooFinanceProvider
from axiom.data.providers.news import NewsProvider

class MacroAgent:
    def __init__(self, provider: Optional[YahooFinanceProvider] = None, news_provider: Optional[NewsProvider] = None):
        self.provider = provider or YahooFinanceProvider()
        self.news_provider = news_provider or NewsProvider()

    def analyze_macro(self, region: str = "US") -> Dict[str, Any]:
        """Fetches macro aggregates, calculates yield curve slope, and retrieves macro news."""
        macro = self.provider.get_macro(region=region)
        news = self.news_provider.get_news(f"{region} economy central bank interest rates inflation", limit=5)

        # Regimes
        slope = macro.yield_curve_slope_10_2
        curve_regime = "NORMAL (Upward Sloping)" if slope and slope > 0.5 else ("FLAT / INVERTED (Recession Warning Signal)" if slope and slope <= 0.0 else "MILDLY NORMAL")

        dxy = macro.dollar_index_dxy
        dollar_regime = "STRONG DOLLAR (Pengetatan Likuiditas Global)" if dxy and dxy > 104 else "MODERATE / WEAK DOLLAR"

        return {
            "region": region,
            "as_of_date": macro.as_of_date,
            "indicators": {
                "treasury_10y_yield_pct": macro.treasury_10y,
                "treasury_2y_reference_pct": macro.treasury_2y,
                "yield_curve_slope_10_2": slope,
                "yield_curve_regime": curve_regime,
                "dollar_index_dxy": dxy,
                "dollar_regime": dollar_regime,
                "crude_oil_wti": macro.crude_oil_wti,
                "gold_price_usd": macro.gold_price,
                "vix_volatility": macro.vix_index
            },
            "macro_news": [n.model_dump() for n in news],
            "source": macro.source.model_dump(),
            "hypothesized_transmission": (
                "Kenaikan suku bunga jangka panjang menaikkan biaya diskonto ekuitas durasi panjang, "
                "sementara penguatan dolar AS cenderung menekan likuiditas emerging markets."
            )
        }
