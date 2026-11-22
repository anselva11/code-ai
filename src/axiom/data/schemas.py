"""Data schemas and strongly typed models for AXIOM AI AGENTS."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FreshnessStatus(str, Enum):
    REAL_TIME = "REAL-TIME"
    DELAYED = "DELAYED"
    END_OF_DAY = "END-OF-DAY"
    HISTORICAL = "HISTORICAL"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"

class SourceRecord(BaseModel):
    name: str
    endpoint_url: str
    retrieval_time_utc: str
    observation_date: str
    asset: str
    interval: str = "1d"
    unit: str = "shares/USD"
    currency: str = "USD"
    freshness: FreshnessStatus = FreshnessStatus.DELAYED
    adjustments: str = "Split & dividend adjusted"
    disclaimer: str = "Data provided for analytical research; not official real-time exchange feed."

class PriceBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: Optional[float] = None

class HistoricalData(BaseModel):
    symbol: str
    asset_type: str = "equity"
    currency: str = "USD"
    source: SourceRecord
    bars: List[PriceBar]

class FundamentalMetrics(BaseModel):
    symbol: str
    company_name: str
    sector: str = "Unknown"
    industry: str = "Unknown"
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    price_to_sales: Optional[float] = None
    price_to_book: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    revenue_growth: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    free_cash_flow: Optional[float] = None
    total_debt: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    dividend_yield: Optional[float] = None
    source: SourceRecord

class MacroData(BaseModel):
    region: str = "US"
    as_of_date: str
    treasury_10y: Optional[float] = None
    treasury_2y: Optional[float] = None
    yield_curve_slope_10_2: Optional[float] = None
    dollar_index_dxy: Optional[float] = None
    crude_oil_wti: Optional[float] = None
    gold_price: Optional[float] = None
    vix_index: Optional[float] = None
    notes: str = ""
    source: SourceRecord

class NewsArticle(BaseModel):
    title: str
    source_name: str
    url: str
    published_date: str
    summary: str

class AuditFinding(BaseModel):
    category: str
    severity: str  # "Tinggi", "Sedang", "Rendah"
    description: str
    mitigation: str
