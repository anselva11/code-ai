"""Risk Agent: VaR/CVaR, tail risk, downside failure modes, and stress scenarios."""
from typing import Dict, Any, List
from axiom.data.schemas import PriceBar
from axiom.analysis.risk import RiskAnalysis

class RiskAgent:
    def analyze_risk(self, bars: List[PriceBar], beta: float = 1.0) -> Dict[str, Any]:
        """Calculates tail risk, VaR, CVaR, and macro stress tests."""
        var_res = RiskAnalysis.calculate_var_cvar(bars)
        current_price = bars[-1].close if bars else 100.0
        stress_scenarios = RiskAnalysis.stress_test(current_price=current_price, beta=beta)

        return {
            "var_metrics": var_res,
            "stress_scenarios": stress_scenarios,
            "downside_assessment": (
                f"Dalam skenario 1-Day VaR 95%, potensi kerugian maksimal berada pada {var_res.get('var_95_1d_pct', 0)}%. "
                f"Skenario tail risk 99% CVaR memproyeksikan rata-rata kerugian ekstrem sebesar {var_res.get('cvar_99_1d_pct', 0)}%."
            )
        }

    def analyze_portfolio_risk(self, holdings: List[Dict[str, Any]], price_series_map: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates portfolio diversification, HHI concentration, and correlation matrix."""
        return RiskAnalysis.analyze_portfolio(holdings, price_series_map)
