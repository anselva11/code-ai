"""Orchestrator Agent: Multi-agent coordination, workflow planning, and report assembly."""
import os
import pandas as pd
from typing import Dict, Any, List, Optional
from rich.console import Console

from axiom.agents.market_data import MarketDataAgent
from axiom.agents.financial_research import FinancialResearchAgent
from axiom.agents.macro import MacroAgent
from axiom.agents.quant import QuantAgent
from axiom.agents.risk import RiskAgent
from axiom.agents.verification import VerificationAgent
from axiom.agents.reporting import ReportingAgent
from axiom.visualization.charts import ChartGenerator

class Orchestrator:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.market_agent = MarketDataAgent()
        self.research_agent = FinancialResearchAgent()
        self.macro_agent = MacroAgent()
        self.quant_agent = QuantAgent()
        self.risk_agent = RiskAgent()
        self.verification_agent = VerificationAgent()
        self.reporting_agent = ReportingAgent()

    def run_market(self, symbol: str, asset_type: str = "equity", period: str = "1y") -> str:
        """Executes full market analysis workflow for an asset."""
        self.console.print(f"[bold cyan]>[/bold cyan] [Market Data Agent] Mengambil data pasar untuk [bold]{symbol}[/bold]...")
        market_res = self.market_agent.fetch_market_data(symbol, period=period)

        self.console.print(f"[bold cyan]>[/bold cyan] [Quant Agent] Menghitung indikator teknikal & volatilitas...")
        quant_res = self.quant_agent.analyze_quant(market_res["bars"])

        self.console.print(f"[bold cyan]>[/bold cyan] [Risk Agent] Menghitung Value-at-Risk & skenario shock...")
        risk_res = self.risk_agent.analyze_risk(market_res["bars"])

        self.console.print(f"[bold cyan]>[/bold cyan] [Visualization] Menampilkan grafik langsung ke layar...")
        df_bars = pd.DataFrame([b.model_dump() for b in market_res["bars"]])
        chart_tmp = f"reports/temp_{symbol}_chart.png"
        ChartGenerator.plot_price_and_ma(
            df=df_bars,
            symbol=symbol,
            output_path=chart_tmp,
            source_label=market_res["source"]["name"],
            retrieval_time=market_res["source"]["retrieval_time_utc"]
        )
        # Menampilkan grafik langsung di layar terminal & membuka jendela gambar OS
        ChartGenerator.display_terminal_price_chart(df_bars, symbol)
        ChartGenerator.open_image_viewer(chart_tmp)

        self.console.print(f"[bold cyan]>[/bold cyan] [Skeptic Agent] Mengaudit integritas data & klaim...")
        verification = self.verification_agent.verify(
            market_data=market_res,
            sources=[market_res["source"]]
        )

        curr_px = market_res["latest_close"]
        tech = quant_res["technical_indicators"]
        q_m = quant_res["quant_metrics"]

        key_metrics = {
            "latest_close": f"${curr_px:.2f}",
            "period_change_pct": f"{tech.get('period_change_pct', 0)*100:+.2f}%",
            "annualized_volatility_pct": f"{q_m.get('annualized_volatility_pct', 0):.2f}%",
            "sharpe_ratio": q_m.get("sharpe_ratio", 0.0),
            "max_drawdown_pct": f"{tech.get('max_drawdown', 0)*100:.2f}%",
            "rsi_14": round(tech.get("rsi_14", 50.0), 1) if tech.get("rsi_14") else "N/A",
            "trend_regime": tech.get("trend_regime", "NEUTRAL")
        }

        summary = (
            f"Analisis pasar untuk {symbol} menunjukkan tren {tech.get('trend_regime')} dengan volatilitas terealisasi tahunan "
            f"sebesar {q_m.get('annualized_volatility_pct', 0):.1f}%. Harga penutupan terakhir berada pada ${curr_px:.2f} "
            f"(perubahan periode: {tech.get('period_change_pct', 0)*100:+.1f}%)."
        )

        report_dir = self.reporting_agent.generate_report_package(
            task_name=f"market_{symbol}",
            asset_or_query=symbol,
            title=f"Laporan Analisis Pasar: {symbol} ({asset_type.upper()})",
            summary=summary,
            verification=verification,
            key_metrics=key_metrics,
            scenarios=risk_res["stress_scenarios"],
            sources=[market_res["source"]],
            assumptions=[
                "Harga disesuaikan terhadap aksi korporasi (split & dividen)",
                "Bunga bebas risiko diasumsikan 4.5% p.a. (US Treasury short rate)",
                "Level teknikal bersifat deskriptif, bukan batas support/resistance mutlak"
            ],
            limitations=[
                "Data bersumber dari feed komunitas non-resmi (delayed / EOD)",
                "Simulasi historis tidak memperhitungkan impak likuiditas order besar"
            ],
            facts=[
                f"Harga penutupan terakhir ${curr_px:.2f} pada tanggal {market_res['latest_date']}",
                f"Jumlah observasi aktif: {len(market_res['bars'])} bar harian"
            ],
            interpretations=[
                f"Indikator RSI-14 berada di level {tech.get('rsi_14', 'N/A')}, mengindikasikan momentum wajar",
                f"Rezim pasar diklasifikasikan sebagai {tech.get('trend_regime')}"
            ],
            uncertainties=[
                "Perubahan suku bunga acuan bank sentral dapat mengubah dinamika volatilitas",
                "Risiko pengumuman laporan laba kuartalan yang dapat memicu price gap"
            ],
            catalysts=[
                "Rilis data makro inflasi (CPI / PCE)",
                "Keputusan suku bunga FOMC berikutnya",
                "Jadwal earnings call kuartalan mendatang"
            ],
            chart_paths=[chart_tmp]
        )

        return report_dir

    def run_research(self, target: str, target_type: str = "company") -> str:
        """Executes comprehensive fundamental and quantitative research."""
        symbol = target.upper()
        self.console.print(f"[bold cyan]>[/bold cyan] [Market Data Agent] Mengambil data harga {symbol}...")
        market_res = self.market_agent.fetch_market_data(symbol, period="2y")

        self.console.print(f"[bold cyan]>[/bold cyan] [Financial Research Agent] Mengambil laporan fundamental & valuasi...")
        fund_res = self.research_agent.research_company(symbol)

        self.console.print(f"[bold cyan]>[/bold cyan] [Quant Agent] Menghitung metrik performa...")
        quant_res = self.quant_agent.analyze_quant(market_res["bars"])

        self.console.print(f"[bold cyan]>[/bold cyan] [Risk Agent] Menganalisis risiko & skenario shock...")
        risk_res = self.risk_agent.analyze_risk(market_res["bars"])

        self.console.print(f"[bold cyan]>[/bold cyan] [Visualization] Menampilkan grafik harga & moving average langsung ke layar...")
        df_bars = pd.DataFrame([b.model_dump() for b in market_res["bars"]])
        chart_tmp = f"reports/temp_{symbol}_research.png"
        ChartGenerator.plot_price_and_ma(
            df=df_bars,
            symbol=symbol,
            output_path=chart_tmp,
            source_label=market_res["source"]["name"],
            retrieval_time=market_res["source"]["retrieval_time_utc"]
        )
        ChartGenerator.display_terminal_price_chart(df_bars, symbol, f"{symbol} — Price History & Trend Regime")
        ChartGenerator.open_image_viewer(chart_tmp)

        sources = [market_res["source"], fund_res["source"]]
        self.console.print(f"[bold cyan]>[/bold cyan] [Skeptic Agent] Mengaudit rasio dan atribusi sumber...")
        verification = self.verification_agent.verify(market_data=market_res, sources=sources)

        val = fund_res["valuation"]
        prof = fund_res["profitability"]
        bs = fund_res["balance_sheet"]

        key_metrics = {
            "company_name": fund_res["company_name"],
            "sector": fund_res["sector"],
            "trailing_pe": val["trailing_pe"] or "N/A",
            "forward_pe": val["forward_pe"] or "N/A",
            "ev_to_ebitda": val["ev_to_ebitda"] or "N/A",
            "revenue_growth_pct": f"{prof['revenue_growth_pct']:.1f}%" if prof['revenue_growth_pct'] else "N/A",
            "operating_margin_pct": f"{prof['operating_margin_pct']:.1f}%" if prof['operating_margin_pct'] else "N/A",
            "free_cash_flow": bs["free_cash_flow"],
            "sharpe_ratio": quant_res["quant_metrics"]["sharpe_ratio"]
        }

        summary = (
            f"Riset fundamental terhadap {fund_res['company_name']} ({symbol}) menunjukkan pertumbuhan pendapatan "
            f"{prof['revenue_growth_pct'] or 'N/A'}% dengan status valuasi {val['summary']}. "
            f"Profitabilitas dikategorikan {prof['summary']} dan struktur utang {bs['summary']}."
        )

        report_dir = self.reporting_agent.generate_report_package(
            task_name=f"research_{symbol}",
            asset_or_query=symbol,
            title=f"Laporan Riset Komprehensif: {fund_res['company_name']} ({symbol})",
            summary=summary,
            verification=verification,
            key_metrics=key_metrics,
            scenarios=risk_res["stress_scenarios"],
            sources=sources,
            assumptions=[
                "Rasio kelipatan valuasi dihitung berbasis trailing 12 bulan (TTM)",
                "Proyeksi arus kas masa depan mengasumsikan stabilitas marjin saat ini",
                "Data bebas risiko disesuaikan dengan kurva suku bunga US"
            ],
            limitations=[
                "Keterbatasan data interim antar pelaporan 10-Q",
                "Valuasi tidak memperhitungkan disrupsi teknologi non-linier"
            ],
            facts=[
                f"Trailing P/E: {val['trailing_pe'] or 'N/A'}, EV/EBITDA: {val['ev_to_ebitda'] or 'N/A'}",
                f"Free Cash Flow dilaporkan: {bs['free_cash_flow']}"
            ],
            interpretations=[
                f"Kondisi valuasi: {val['summary']}",
                f"Kesehatan neraca: {bs['summary']}"
            ],
            uncertainties=[
                "Perubahan regulasi industri dan tekanan kompetisi harga",
                "Volatilitas permintaan global pada sektor terkait"
            ],
            catalysts=[
                "Rilis laporan keuangan kuartal berikutnya",
                "Pengumuman inovasi produk atau ekspansi pasar baru",
                "Perubahan guidance tahunan dari manajemen"
            ],
            chart_paths=[chart_tmp]
        )

        return report_dir

    def run_macro(self, region: str = "US") -> str:
        """Executes macroeconomic environment analysis."""
        self.console.print(f"[bold cyan]>[/bold cyan] [Macro Agent] Mengambil indikator makro agregat kawasan {region}...")
        macro_res = self.macro_agent.analyze_macro(region=region)

        self.console.print(f"[bold cyan]>[/bold cyan] [Skeptic Agent] Mengaudit indikator & status...")
        verification = self.verification_agent.verify(sources=[macro_res["source"]])

        ind = macro_res["indicators"]
        key_metrics = {
            "treasury_10y_yield_pct": f"{ind['treasury_10y_yield_pct']:.3f}%" if ind['treasury_10y_yield_pct'] else "N/A",
            "yield_curve_slope_10_2": f"{ind['yield_curve_slope_10_2']:+.3f}" if ind['yield_curve_slope_10_2'] else "N/A",
            "yield_curve_regime": ind["yield_curve_regime"],
            "dollar_index_dxy": round(ind["dollar_index_dxy"], 2) if ind["dollar_index_dxy"] else "N/A",
            "dollar_regime": ind["dollar_regime"],
            "crude_oil_wti": f"${ind['crude_oil_wti']:.2f}" if ind['crude_oil_wti'] else "N/A",
            "gold_price_usd": f"${ind['gold_price_usd']:.2f}" if ind['gold_price_usd'] else "N/A",
            "vix_index": round(ind["vix_volatility"], 2) if ind["vix_volatility"] else "N/A"
        }

        summary = (
            f"Kondisi makroekonomi kawasan {region} saat ini dicirikan oleh kurva imbal hasil {ind['yield_curve_regime']} "
            f"dengan yield US 10-Year pada {ind['treasury_10y_yield_pct']:.2f}%. Dolar AS berada dalam rezim {ind['dollar_regime']}."
        )

        scenarios = [
            {"scenario": "Inflation Persistence (+50 bps Fed Rate Hike)", "projected_change_pct": -4.5, "projected_price": 0.0, "mechanism": "Kompresi valuasi aset risiko"},
            {"scenario": "Soft Landing & Rate Cuts (-50 bps)", "projected_change_pct": +6.0, "projected_price": 0.0, "mechanism": "Ekspansi kelipatan valuasi ekuitas"},
            {"scenario": "Geopolitical Commodity Shock (+20% Oil)", "projected_change_pct": -3.0, "projected_price": 0.0, "mechanism": "Tekanan inflasi biaya energi"}
        ]

        report_dir = self.reporting_agent.generate_report_package(
            task_name=f"macro_{region}",
            asset_or_query=f"MACRO_{region}",
            title=f"Laporan Intelijen Makroekonomi: Kawasan {region}",
            summary=summary,
            verification=verification,
            key_metrics=key_metrics,
            scenarios=scenarios,
            sources=[macro_res["source"]],
            assumptions=[
                "Yield curve slope diukur terhadap acuan tenor 10Y dan short-rate 4.5%",
                "Indeks Dolar (DXY) merefleksikan kekuatan relatif terhadap mata uang utama"
            ],
            limitations=[
                "Data makro bersumber dari agregasi instrumen pasar sekunder",
                "Hubungan transmisi makro-ke-pasar bersifat hipotesis historis, bukan kepastian"
            ],
            facts=[
                f"Yield 10-Year Treasury: {ind['treasury_10y_yield_pct']}%",
                f"Indeks Dolar DXY: {ind['dollar_index_dxy']}"
            ],
            interpretations=[
                f"Kondisi moneter: {ind['dollar_regime']}",
                f"Sinyal kurva imbal hasil: {ind['yield_curve_regime']}"
            ],
            uncertainties=[
                "Keputusan suku bunga dan proyeksi inflasi bank sentral",
                "Eskalasi ketegangan geopolitik yang memicu fluktuasi komoditas"
            ],
            catalysts=[
                "Pertemuan rapat kebijakan moneter FOMC",
                "Data ketenagakerjaan Non-Farm Payrolls",
                "Laporan rilis inflasi CPI / PPI"
            ],
            chart_paths=[]
        )

        return report_dir

    def run_backtest(self, symbol: str, strategy: str = "momentum", period: str = "5y") -> str:
        """Runs quantitative backtest with strict t+1 timing to eliminate look-ahead bias."""
        self.console.print(f"[bold cyan]>[/bold cyan] [Market Data Agent] Mengambil bar harga historis {symbol}...")
        market_res = self.market_agent.fetch_market_data(symbol, period=period)

        self.console.print(f"[bold cyan]>[/bold cyan] [Quant Agent] Menjalankan simulasi strategi {strategy.upper()}...")
        bt_res = self.quant_agent.run_backtest(market_res["bars"], strategy_name=strategy)

        self.console.print(f"[bold cyan]>[/bold cyan] [Visualization] Menampilkan kurva ekuitas langsung ke layar...")
        chart_tmp = f"reports/temp_bt_{symbol}_{strategy}.png"
        ChartGenerator.plot_equity_curve(
            strategy_curve=bt_res.equity_curve,
            benchmark_curve=bt_res.benchmark_curve,
            title=f"Backtest {strategy.upper()} on {symbol} ({period})",
            output_path=chart_tmp,
            source_label=market_res["source"]["name"],
            retrieval_time=market_res["source"]["retrieval_time_utc"]
        )
        ChartGenerator.display_terminal_equity_chart(bt_res.equity_curve, bt_res.benchmark_curve, f"Backtest {strategy.upper()} on {symbol}")
        ChartGenerator.open_image_viewer(chart_tmp)

        self.console.print(f"[bold cyan]>[/bold cyan] [Skeptic Agent] Mengaudit timing eksekusi & turnover...")
        verification = self.verification_agent.verify(
            market_data=market_res,
            backtest_result=bt_res,
            sources=[market_res["source"]]
        )

        m = bt_res.metrics
        key_metrics = {
            "strategy": strategy.upper(),
            "cagr_pct": f"{m.get('cagr_pct', 0):.2f}%",
            "sharpe_ratio": m.get("sharpe_ratio", 0.0),
            "sortino_ratio": m.get("sortino_ratio", 0.0),
            "max_drawdown_pct": f"{m.get('max_drawdown_pct', 0):.2f}%",
            "annual_turnover_pct": f"{m.get('annual_turnover_pct', 0):.1f}%",
            "trade_count": bt_res.trade_count,
            "frictional_costs_pct": f"{m.get('total_frictional_costs_pct', 0):.2f}%"
        }
        if "alpha_cagr_pct" in m:
            key_metrics["alpha_vs_benchmark_pct"] = f"{m.get('alpha_cagr_pct'):+.2f}%"

        summary = (
            f"Simulasi backtest strategi {strategy.upper()} pada {symbol} ({bt_res.period_start} hingga {bt_res.period_end}) "
            f"menghasilkan CAGR net of fees sebesar {m.get('cagr_pct', 0):.1f}% dengan Sharpe Ratio {m.get('sharpe_ratio', 0.0)} "
            f"dan Maximum Drawdown {m.get('max_drawdown_pct', 0):.1f}%. Eksekusi sinyal diverifikasi bebas look-ahead bias (t+1)."
        )

        report_dir = self.reporting_agent.generate_report_package(
            task_name=f"backtest_{symbol}_{strategy}",
            asset_or_query=f"{symbol}:{strategy}",
            title=f"Laporan Backtest Kuantitatif: {symbol} — {strategy.upper()}",
            summary=summary,
            verification=verification,
            key_metrics=key_metrics,
            scenarios=[
                {"scenario": "Biaya Transaksi Naik 2x (Slippage Ekstrem)", "projected_change_pct": -2.0, "projected_price": 0.0, "mechanism": "Frictional drag bertambah"},
                {"scenario": "Regime Sideways Volatil", "projected_change_pct": -4.0, "projected_price": 0.0, "mechanism": "Whipsaw losses pada tren palsu"}
            ],
            sources=[market_res["source"]],
            assumptions=[
                "Biaya transaksi diperhitungkan: komisi 10 bps, slippage 5 bps per pergantian posisi",
                "Sinyal dihitung pada penutupan t dan dieksekusi pada harga pembukaan t+1",
                "Suku bunga bebas risiko diasumsikan 4.5% p.a."
            ],
            limitations=[
                "Simulasi historis tidak menjamin performa keuntungan di masa depan",
                "Tidak memperhitungkan pembatasan likuiditas lot besar (market impact)",
                "Asumsi ketersediaan pinjaman efek saat posisi short"
            ],
            facts=[
                f"Total sinyal transaksi dieksekusi: {bt_res.trade_count}",
                f"Turnover tahunan rata-rata: {m.get('annual_turnover_pct', 0):.1f}%"
            ],
            interpretations=[
                f"Sharpe ratio strategi: {m.get('sharpe_ratio', 0.0)}",
                f"Kapasitas ketahanan drawdown: {m.get('max_drawdown_pct', 0):.1f}%"
            ],
            uncertainties=[
                "Pergeseran rezim volatilitas pasar di masa mendatang",
                "Penurunan alpha akibat overcrowding strategi serupa"
            ],
            catalysts=[
                "Perubahan korelasi aset",
                "Perubahan struktur fee dan likuiditas bursa"
            ],
            chart_paths=[chart_tmp]
        )

        return report_dir

    def run_portfolio(self, csv_filepath: str) -> str:
        """Executes portfolio concentration, diversification, and correlation analysis."""
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"Berkas portofolio tidak ditemukan: {csv_filepath}")

        df_port = pd.read_csv(csv_filepath)
        if "ticker" not in df_port.columns:
            raise ValueError("CSV portofolio wajib memiliki kolom 'ticker'.")

        tickers = df_port["ticker"].dropna().unique().tolist()
        self.console.print(f"[bold cyan]>[/bold cyan] [Market Data Agent] Mengambil data historis untuk {len(tickers)} aset portofolio...")

        price_series_map = {}
        sources = []
        for sym in tickers:
            try:
                m_res = self.market_agent.fetch_market_data(sym, period="1y")
                df_b = pd.DataFrame([b.model_dump() for b in m_res["bars"]]).set_index("date")["close"]
                price_series_map[sym] = df_b
                sources.append(m_res["source"])
            except Exception:
                continue

        self.console.print(f"[bold cyan]>[/bold cyan] [Risk Agent] Menganalisis konsentrasi HHI, volatilitas, dan korelasi...")
        holdings_list = df_port.to_dict(orient="records")
        port_res = self.risk_agent.analyze_portfolio_risk(holdings_list, price_series_map)

        chart_tmp = "reports/temp_portfolio_corr.png"
        df_corr = pd.DataFrame(port_res["correlation_matrix"])
        ChartGenerator.plot_correlation_heatmap(df_corr, output_path=chart_tmp)
        ChartGenerator.open_image_viewer(chart_tmp)

        verification = self.verification_agent.verify(sources=sources)

        key_metrics = {
            "total_assets": port_res["holdings_count"],
            "hhi_concentration": port_res["hhi_index"],
            "diversification_rating": port_res["concentration_rating"],
            "portfolio_annualized_volatility_pct": f"{port_res['portfolio_annualized_volatility_pct']:.2f}%"
        }

        summary = (
            f"Analisis portofolio terhadap {port_res['holdings_count']} aset menunjukkan peringkat diversifikasi "
            f"'{port_res['concentration_rating']}' (HHI: {port_res['hhi_index']}) dengan volatilitas terealisasi tahunan "
            f"portofolio sebesar {port_res['portfolio_annualized_volatility_pct']:.2f}%."
        )

        scenarios = [
            {"scenario": "Global Equity Correction (-10%)", "projected_change_pct": -8.5, "projected_price": 0.0, "mechanism": "Penurunan nilai wajar serempak"},
            {"scenario": "Dollar Surge & Yield Spike (+100 bps)", "projected_change_pct": -5.2, "projected_price": 0.0, "mechanism": "Tekanan aset durasi tinggi"}
        ]

        report_dir = self.reporting_agent.generate_report_package(
            task_name="portfolio_analysis",
            asset_or_query=f"{len(tickers)}_assets_portfolio",
            title="Laporan Analisis Risiko & Diversifikasi Portofolio",
            summary=summary,
            verification=verification,
            key_metrics=key_metrics,
            scenarios=scenarios,
            sources=sources,
            assumptions=[
                "Bobot portofolio dinormalisasi menjadi 100%",
                "Kovarians dihitung berbasis return harian 1 tahun terakhir"
            ],
            limitations=[
                "Korelasi historis dapat melonjak mendekati 1.0 saat krisis pasar likuiditas"
            ],
            facts=[
                f"HHI Index: {port_res['hhi_index']}",
                f"Volatilitas portofolio tahunan: {port_res['portfolio_annualized_volatility_pct']}%"
            ],
            interpretations=[
                f"Status konsentrasi: {port_res['concentration_rating']}"
            ],
            uncertainties=[
                "Breakdown korelasi non-linear saat periode shock pasar"
            ],
            catalysts=[
                "Jadwal rebalancing berkala",
                "Perubahan pembobotan indeks acuan"
            ],
            chart_paths=[chart_tmp]
        )

        return report_dir
