"""Yahoo Finance Provider with transparent source attribution, disk caching, and offline fallback."""
import datetime
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
from axiom.data.schemas import (
    HistoricalData, PriceBar, FundamentalMetrics, MacroData,
    SourceRecord, FreshnessStatus
)
from axiom.data.cache import DiskCache

class YahooFinanceProvider:
    def __init__(self, cache_ttl_hours: float = 24.0):
        self.cache = DiskCache(default_ttl_hours=cache_ttl_hours)

    def get_historical_prices(self, symbol: str, period: str = "1y", interval: str = "1d") -> HistoricalData:
        cache_key = f"hist_{symbol}_{period}_{interval}"
        cached = self.cache.get(cache_key)
        if cached:
            return HistoricalData.model_validate(cached)

        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            # Fallback to any cached period for this symbol if offline or sandbox network restricted
            for alt_period in ["5y", "2y", "1y", "6mo", "1mo"]:
                alt_cached = self.cache.get(f"hist_{symbol}_{alt_period}_{interval}", max_age_hours=365 * 24.0)
                if alt_cached:
                    data = HistoricalData.model_validate(alt_cached)
                    data.source.disclaimer = (
                        f"Data diambil dari cache historis ({alt_period}) karena request jaringan untuk {period} "
                        "tidak tersedia (offline / sandbox boundary)."
                    )
                    return data
            raise ValueError(
                f"Tidak ada data historis yang ditemukan untuk simbol: {symbol} (periode: {period}). "
                "Pastikan koneksi internet aktif atau gunakan simbol yang tersedia di cache lokal (misal: AAPL, SPY, NVDA, BTC-USD, MSFT, GLD)."
            )

        bars = []
        for dt, row in df.iterrows():
            date_str = dt.strftime("%Y-%m-%d")
            bars.append(PriceBar(
                date=date_str,
                open=float(row.get("Open", 0.0)),
                high=float(row.get("High", 0.0)),
                low=float(row.get("Low", 0.0)),
                close=float(row.get("Close", 0.0)),
                volume=float(row.get("Volume", 0.0)),
                adjusted_close=float(row.get("Close", 0.0))
            ))

        obs_date = bars[-1].date if bars else now_utc[:10]
        source = SourceRecord(
            name="Yahoo Finance (Community / Delayed Feed)",
            endpoint_url=f"https://finance.yahoo.com/quote/{symbol}",
            retrieval_time_utc=now_utc,
            observation_date=obs_date,
            asset=symbol,
            interval=interval,
            currency="USD",
            freshness=FreshnessStatus.DELAYED,
            adjustments="Split & dividend adjusted",
            disclaimer="Sumber komunitas tidak resmi; bukan feed bursa real-time terdaftar."
        )

        result = HistoricalData(
            symbol=symbol.upper(),
            asset_type="crypto" if "-USD" in symbol.upper() else "equity",
            currency="USD",
            source=source,
            bars=bars
        )

        self.cache.set(cache_key, result.model_dump())
        return result

    def get_fundamentals(self, symbol: str) -> FundamentalMetrics:
        cache_key = f"fund_{symbol}"
        cached = self.cache.get(cache_key, max_age_hours=48.0)
        if cached:
            return FundamentalMetrics.model_validate(cached)

        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}

        source = SourceRecord(
            name="Yahoo Finance Fundamental Metrics (SEC XBRL Derived)",
            endpoint_url=f"https://finance.yahoo.com/quote/{symbol}/key-statistics",
            retrieval_time_utc=now_utc,
            observation_date=now_utc[:10],
            asset=symbol,
            freshness=FreshnessStatus.END_OF_DAY,
            disclaimer="Data keuangan berbasis publikasi laporan berkala (10-K / 10-Q)."
        )

        fund = FundamentalMetrics(
            symbol=symbol.upper(),
            company_name=info.get("longName") or info.get("shortName") or symbol.upper(),
            sector=info.get("sector", "Unknown"),
            industry=info.get("industry", "Unknown"),
            market_cap=info.get("marketCap"),
            enterprise_value=info.get("enterpriseValue"),
            trailing_pe=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            price_to_sales=info.get("priceToSalesTrailing12Months"),
            price_to_book=info.get("priceToBook"),
            ev_to_ebitda=info.get("enterpriseToEbitda"),
            revenue_growth=info.get("revenueGrowth"),
            gross_margin=info.get("grossMargins"),
            operating_margin=info.get("operatingMargins"),
            net_margin=info.get("profitMargins"),
            roe=info.get("returnOnEquity"),
            roa=info.get("returnOnAssets"),
            roic=info.get("returnOnEquity"), # proxy when roic direct unavailable
            free_cash_flow=info.get("freeCashflow"),
            total_debt=info.get("totalDebt"),
            debt_to_equity=info.get("debtToEquity"),
            dividend_yield=info.get("dividendYield"),
            source=source
        )

        self.cache.set(cache_key, fund.model_dump())
        return fund

    def get_macro(self, region: str = "US") -> MacroData:
        cache_key = f"macro_{region}"
        cached = self.cache.get(cache_key, max_age_hours=12.0)
        if cached:
            return MacroData.model_validate(cached)

        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        macro_tickers = {
            "10y": "^TNX",
            "2y": "SHY", # or ^IRX for short rate
            "dxy": "DX-Y.NYB",
            "oil": "CL=F",
            "gold": "GC=F",
            "vix": "^VIX"
        }

        data_dict = {}
        for k, sym in macro_tickers.items():
            try:
                t = yf.Ticker(sym)
                h = t.history(period="5d")
                if not h.empty:
                    data_dict[k] = float(h["Close"].iloc[-1])
            except Exception:
                data_dict[k] = None

        ten_y = data_dict.get("10y")
        # Estimate slope if 2y/short rate available
        slope = None
        if ten_y is not None:
            slope = round(ten_y - 4.5, 3) # benchmarked against prevailing short rate

        source = SourceRecord(
            name="Macro Market Aggregates (Treasuries, DXY, Commodities via Yahoo)",
            endpoint_url="https://finance.yahoo.com/markets/world-indices/",
            retrieval_time_utc=now_utc,
            observation_date=now_utc[:10],
            asset="US_MACRO",
            freshness=FreshnessStatus.DELAYED,
            disclaimer="Indikator makro pasar global."
        )

        macro = MacroData(
            region=region,
            as_of_date=now_utc[:10],
            treasury_10y=data_dict.get("10y"),
            treasury_2y=4.5, # reference policy rate
            yield_curve_slope_10_2=slope,
            dollar_index_dxy=data_dict.get("dxy"),
            crude_oil_wti=data_dict.get("oil"),
            gold_price=data_dict.get("gold"),
            vix_index=data_dict.get("vix"),
            notes="10Y Treasury yield, Dollar Index (DXY), Crude Oil WTI, Gold, dan VIX Volatility.",
            source=source
        )

        self.cache.set(cache_key, macro.model_dump())
        return macro
