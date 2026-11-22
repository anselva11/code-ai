"""Quant Agent: Statistical factors, quantitative metrics, and backtest orchestrator."""
from typing import Dict, Any, List, Optional
from axiom.data.schemas import PriceBar
from axiom.analysis.quant import QuantAnalysis
from axiom.analysis.technical import TechnicalAnalysis
from axiom.backtesting.engine import BacktestEngine, BacktestResult
from axiom.backtesting.strategies import MomentumStrategy, MACrossoverStrategy, MeanReversionStrategy, BuyAndHoldStrategy

class QuantAgent:
    def __init__(self, fee_rate: float = 0.0010, slippage_rate: float = 0.0005, rf_rate: float = 0.045):
        self.engine = BacktestEngine(fee_rate=fee_rate, slippage_rate=slippage_rate, rf_rate=rf_rate)
        self.rf_rate = rf_rate

    def analyze_quant(self, bars: List[PriceBar], benchmark_bars: Optional[List[PriceBar]] = None) -> Dict[str, Any]:
        """Calculates institutional quantitative metrics and technical factors."""
        quant_metrics = QuantAnalysis.calculate_metrics(bars, rf_rate=self.rf_rate)
        tech_metrics = TechnicalAnalysis.analyze(bars)

        bench_comparison = {}
        if benchmark_bars:
            bench_comparison = QuantAnalysis.compare_benchmark(bars, benchmark_bars)

        return {
            "quant_metrics": quant_metrics,
            "technical_indicators": tech_metrics,
            "benchmark_comparison": bench_comparison
        }

    def run_backtest(
        self,
        bars: List[PriceBar],
        strategy_name: str = "momentum",
        benchmark_bars: Optional[List[PriceBar]] = None
    ) -> BacktestResult:
        """Runs backtest with strict t+1 execution to eliminate look-ahead bias."""
        strat = MomentumStrategy()
        if strategy_name.lower() in ("ma", "crossover", "trend"):
            strat = MACrossoverStrategy()
        elif strategy_name.lower() in ("mean_reversion", "rsi"):
            strat = MeanReversionStrategy()
        elif strategy_name.lower() in ("buy_and_hold", "benchmark"):
            strat = BuyAndHoldStrategy()

        return self.engine.run(bars, strategy=strat, benchmark_bars=benchmark_bars, strategy_name=strategy_name)
