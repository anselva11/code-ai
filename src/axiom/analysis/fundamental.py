"""Fundamental metrics and financial statement synthesis."""
from typing import Dict, Any
from axiom.data.schemas import FundamentalMetrics

class FundamentalAnalysis:
    @staticmethod
    def evaluate(fund: FundamentalMetrics) -> Dict[str, Any]:
        """Evaluates valuation, profitability margins, debt health, and growth."""
        pe = fund.trailing_pe
        ps = fund.price_to_sales
        pb = fund.price_to_book
        ev_ebitda = fund.ev_to_ebitda
        rev_growth = fund.revenue_growth
        net_margin = fund.net_margin
        fcf = fund.free_cash_flow
        debt_to_eq = fund.debt_to_equity

        valuation_summary = "Valuasi Premium" if pe and pe > 30 else ("Valuasi Moderat" if pe and pe > 15 else "Valuasi Value / Murah")
        profitability_summary = "Profitabilitas Tinggi" if net_margin and net_margin > 0.20 else ("Profitabilitas Sehat" if net_margin and net_margin > 0.08 else "Margin Tipis / Merugi")
        debt_summary = "Neraca Konservatif (Rendah Utang)" if debt_to_eq and debt_to_eq < 50 else ("Utang Moderat" if debt_to_eq and debt_to_eq < 150 else "Leverage Tinggi")

        return {
            "symbol": fund.symbol,
            "company_name": fund.company_name,
            "sector": fund.sector,
            "industry": fund.industry,
            "market_cap_formatted": f"${fund.market_cap / 1e9:.2f}B" if fund.market_cap else "N/A",
            "trailing_pe": pe,
            "forward_pe": fund.forward_pe,
            "price_to_sales": ps,
            "price_to_book": pb,
            "ev_to_ebitda": ev_ebitda,
            "revenue_growth_pct": float(rev_growth * 100) if rev_growth is not None else None,
            "gross_margin_pct": float(fund.gross_margin * 100) if fund.gross_margin is not None else None,
            "operating_margin_pct": float(fund.operating_margin * 100) if fund.operating_margin is not None else None,
            "net_margin_pct": float(net_margin * 100) if net_margin is not None else None,
            "roe_pct": float(fund.roe * 100) if fund.roe is not None else None,
            "fcf_formatted": f"${fcf / 1e9:.2f}B" if fcf else "N/A",
            "debt_to_equity": debt_to_eq,
            "dividend_yield_pct": float(fund.dividend_yield * 100) if fund.dividend_yield else 0.0,
            "valuation_summary": valuation_summary,
            "profitability_summary": profitability_summary,
            "debt_summary": debt_summary
        }
