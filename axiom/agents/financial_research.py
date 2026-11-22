"""Financial Research Agent: Filings, earnings, margins, valuation, and balance sheet health."""
from typing import Dict, Any, Optional
from axiom.data.providers.yahoo import YahooFinanceProvider
from axiom.analysis.fundamental import FundamentalAnalysis

class FinancialResearchAgent:
    def __init__(self, provider: Optional[YahooFinanceProvider] = None):
        self.provider = provider or YahooFinanceProvider()

    def research_company(self, symbol: str) -> Dict[str, Any]:
        """Fetches fundamental data and synthesizes financial metrics."""
        fund = self.provider.get_fundamentals(symbol)
        evaluation = FundamentalAnalysis.evaluate(fund)

        return {
            "symbol": fund.symbol,
            "company_name": fund.company_name,
            "sector": fund.sector,
            "industry": fund.industry,
            "valuation": {
                "trailing_pe": fund.trailing_pe,
                "forward_pe": fund.forward_pe,
                "price_to_sales": fund.price_to_sales,
                "price_to_book": fund.price_to_book,
                "ev_to_ebitda": fund.ev_to_ebitda,
                "summary": evaluation["valuation_summary"]
            },
            "profitability": {
                "revenue_growth_pct": evaluation["revenue_growth_pct"],
                "gross_margin_pct": evaluation["gross_margin_pct"],
                "operating_margin_pct": evaluation["operating_margin_pct"],
                "net_margin_pct": evaluation["net_margin_pct"],
                "roe_pct": evaluation["roe_pct"],
                "summary": evaluation["profitability_summary"]
            },
            "balance_sheet": {
                "free_cash_flow": evaluation["fcf_formatted"],
                "debt_to_equity": evaluation["debt_to_equity"],
                "dividend_yield_pct": evaluation["dividend_yield_pct"],
                "summary": evaluation["debt_summary"]
            },
            "source": fund.source.model_dump()
        }
