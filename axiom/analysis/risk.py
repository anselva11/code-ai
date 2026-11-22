"""Risk analytics: Value at Risk (VaR), CVaR, Tail Risk, and Portfolio Stress Testing."""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats
from axiom.data.schemas import PriceBar

class RiskAnalysis:
    @staticmethod
    def calculate_var_cvar(bars: List[PriceBar]) -> Dict[str, Any]:
        """Calculates 1-Day and 10-Day VaR (95%, 99%) and Expected Shortfall (CVaR)."""
        if not bars or len(bars) < 20:
            return {"error": "Observasi tidak cukup untuk kalkulasi VaR."}

        df = pd.DataFrame([b.model_dump() for b in bars])
        returns = df["close"].pct_change().dropna()

        # Historical VaR (Percentile of empirical loss distribution)
        var_95_1d = float(np.percentile(returns, 5))
        var_99_1d = float(np.percentile(returns, 1))

        # CVaR (Expected Shortfall: mean of returns below VaR)
        cvar_95_1d = float(returns[returns <= var_95_1d].mean())
        cvar_99_1d = float(returns[returns <= var_99_1d].mean())

        # Parametric (Gaussian) VaR
        mu = returns.mean()
        sigma = returns.std()
        p_var_95 = float(mu - 1.645 * sigma)
        p_var_99 = float(mu - 2.326 * sigma)

        # 10-Day scaling (Square root of time rule)
        var_95_10d = float(var_95_1d * np.sqrt(10))
        var_99_10d = float(var_99_1d * np.sqrt(10))

        return {
            "var_95_1d_pct": round(abs(var_95_1d) * 100, 2),
            "var_99_1d_pct": round(abs(var_99_1d) * 100, 2),
            "cvar_95_1d_pct": round(abs(cvar_95_1d) * 100, 2),
            "cvar_99_1d_pct": round(abs(cvar_99_1d) * 100, 2),
            "parametric_var_95_pct": round(abs(p_var_95) * 100, 2),
            "parametric_var_99_pct": round(abs(p_var_99) * 100, 2),
            "var_95_10d_pct": round(abs(var_95_10d) * 100, 2),
            "var_99_10d_pct": round(abs(var_99_10d) * 100, 2),
            "tail_risk_flag": "TINGGI" if abs(cvar_99_1d) > 0.08 else ("SEDANG" if abs(cvar_99_1d) > 0.04 else "RENDAH")
        }

    @staticmethod
    def stress_test(current_price: float, beta: float = 1.0) -> List[Dict[str, Any]]:
        """Simulates asset sensitivity to predefined macro and market stress scenarios."""
        scenarios = [
            ("Equity Crash (Global -15%)", -0.15 * beta, "Penurunan valuasi serentak akibat shock sistemik."),
            ("Rate Spike (+100 bps Yield Shock)", -0.06 * max(beta, 0.5), "Peningkatan biaya modal dan kompresi kelipatan P/E."),
            ("Oil Supply Disruption (+25% WTI)", -0.04, "Kenaikan inflasi biaya input energi."),
            ("Liquidity Freeze / Credit Crunch", -0.10 * max(beta, 0.8), "Pelebaran credit spread dan pengetatan margin pinjaman.")
        ]
        results = []
        for name, impact_pct, desc in scenarios:
            projected_price = current_price * (1.0 + impact_pct)
            results.append({
                "scenario": name,
                "projected_change_pct": round(impact_pct * 100, 2),
                "projected_price": round(projected_price, 2),
                "mechanism": desc
            })
        return results

    @staticmethod
    def analyze_portfolio(holdings: List[Dict[str, Any]], price_series_map: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Analyzes multi-asset portfolio weights, HHI concentration, and correlation matrix."""
        df_weights = pd.DataFrame(holdings)
        if "portfolio_weight" not in df_weights.columns and "quantity" in df_weights.columns:
            # Estimate weights from latest prices
            values = []
            for _, row in df_weights.iterrows():
                sym = row["ticker"]
                qty = float(row["quantity"])
                px = price_series_map[sym].iloc[-1] if sym in price_series_map else 1.0
                values.append(qty * px)
            total_val = sum(values) if sum(values) > 0 else 1.0
            df_weights["portfolio_weight"] = [v / total_val for v in values]

        weights = df_weights.set_index("ticker")["portfolio_weight"]
        weights = weights / weights.sum() # Normalize

        # Herfindahl-Hirschman Index (Concentration)
        hhi = float((weights ** 2).sum() * 10000)
        conc_label = "Sangat Terkonsentrasi" if hhi > 2500 else ("Konsentrasi Moderat" if hhi > 1500 else "Terdiversifikasi Baik")

        # Correlation Matrix
        valid_series = {k: s for k, s in price_series_map.items() if k in weights.index}
        df_prices = pd.DataFrame(valid_series).dropna()
        returns = df_prices.pct_change().dropna()
        corr_matrix = returns.corr().round(2).to_dict()

        # Portfolio Volatility
        cov_matrix = returns.cov() * 252
        w_vec = np.array([weights.get(col, 0.0) for col in returns.columns])
        port_vol = float(np.sqrt(np.dot(w_vec.T, np.dot(cov_matrix, w_vec)))) if len(w_vec) > 0 else 0.0

        return {
            "holdings_count": len(weights),
            "hhi_index": round(hhi, 1),
            "concentration_rating": conc_label,
            "weights": {k: round(float(v) * 100, 2) for k, v in weights.items()},
            "portfolio_annualized_volatility_pct": round(port_vol * 100, 2),
            "correlation_matrix": corr_matrix
        }
