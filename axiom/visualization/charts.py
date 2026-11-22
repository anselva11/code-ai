"""Institutional high-resolution dark-theme financial chart generator."""
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import sys
import subprocess
from typing import Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
import plotext as pltx

class ChartGenerator:
    DARK_BG = "#0e1117"
    PANEL_BG = "#161b22"
    TEXT_COLOR = "#e0e6ed"
    GRID_COLOR = "#30363d"
    ACCENT_CYAN = "#00b4d8"
    ACCENT_GREEN = "#06d6a0"
    ACCENT_GOLD = "#ffd166"
    ACCENT_RED = "#ef476f"

    @classmethod
    def display_terminal_price_chart(cls, df: pd.DataFrame, symbol: str, title: str = "") -> None:
        """Renders visual ASCII/Unicode chart directly into the terminal screen."""
        if df.empty or len(df) < 5:
            return
        closes = df["close"].tolist()
        pltx.clf()
        pltx.theme("dark")
        pltx.plot(closes, label=f"{symbol} Close", color="cyan")
        if len(closes) >= 50:
            sma50 = df["close"].rolling(50).mean().fillna(closes[0]).tolist()
            pltx.plot(sma50, label="SMA 50", color="yellow")
        if len(closes) >= 200:
            sma200 = df["close"].rolling(200).mean().fillna(closes[0]).tolist()
            pltx.plot(sma200, label="SMA 200", color="red")
        pltx.title(title or f"{symbol} — Price History & Moving Averages (Direct Terminal Display)")
        pltx.xlabel("Observasi (Hari)")
        pltx.ylabel("Harga (USD)")
        pltx.plotsize(90, 20)
        pltx.show()
        print("")

    @classmethod
    def display_terminal_equity_chart(cls, strategy_curve: pd.Series, benchmark_curve: Optional[pd.Series] = None, title: str = "") -> None:
        """Renders visual ASCII/Unicode backtest equity curve directly into the terminal screen."""
        pltx.clf()
        pltx.theme("dark")
        pltx.plot(strategy_curve.tolist(), label="Strategy (Net of Fees)", color="green")
        if benchmark_curve is not None and not benchmark_curve.empty:
            pltx.plot(benchmark_curve.tolist(), label="Benchmark", color="cyan")
        pltx.title(title or "Backtest Equity Curve ($1.00 Base — Direct Terminal Display)")
        pltx.xlabel("Observasi (Hari)")
        pltx.ylabel("Nilai Portofolio")
        pltx.plotsize(90, 20)
        pltx.show()
        print("")

    @classmethod
    def open_image_viewer(cls, image_path: str) -> None:
        """Automatically opens the high-resolution PNG image in OS default viewer window."""
        if not os.path.exists(image_path):
            return
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", image_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", image_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == "win32":
                os.startfile(image_path)
        except Exception:
            pass

    @classmethod
    def _apply_theme(cls, ax, title: str, subtitle: str, ylabel: str = ""):
        ax.set_facecolor(cls.PANEL_BG)
        ax.tick_params(colors=cls.TEXT_COLOR, labelsize=10)
        ax.grid(True, color=cls.GRID_COLOR, linestyle="--", linewidth=0.7, alpha=0.7)
        for spine in ax.spines.values():
            spine.set_color(cls.GRID_COLOR)
        if ylabel:
            ax.set_ylabel(ylabel, color=cls.TEXT_COLOR, fontsize=11, fontweight="bold")
        ax.set_title(f"{title}\n{subtitle}", color=cls.TEXT_COLOR, fontsize=13, fontweight="bold", pad=12, loc="left")

    @classmethod
    def plot_price_and_ma(
        cls,
        df: pd.DataFrame,
        symbol: str,
        output_path: str,
        source_label: str = "Yahoo Finance",
        retrieval_time: str = ""
    ) -> str:
        """Renders 1600px price history chart with 50 and 200 SMA."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(16, 9), dpi=150,
            facecolor=cls.DARK_BG,
            gridspec_kw={"height_ratios": [3, 1]}
        )

        dates = pd.to_datetime(df["date"])
        closes = df["close"]

        # Price & Moving Averages
        ax1.plot(dates, closes, label=f"{symbol} Close", color=cls.ACCENT_CYAN, linewidth=1.8)
        if len(closes) >= 50:
            sma50 = closes.rolling(50).mean()
            ax1.plot(dates, sma50, label="50-Day SMA", color=cls.ACCENT_GOLD, linewidth=1.4, linestyle="--")
        if len(closes) >= 200:
            sma200 = closes.rolling(200).mean()
            ax1.plot(dates, sma200, label="200-Day SMA", color=cls.ACCENT_RED, linewidth=1.4, linestyle=":")

        sub = f"Source: {source_label} | As of: {dates.iloc[-1].strftime('%Y-%m-%d')} | Retrieved UTC: {retrieval_time}"
        cls._apply_theme(ax1, f"{symbol} — Price History & Trend Regime", sub, "Price (USD)")
        ax1.legend(facecolor=cls.PANEL_BG, edgecolor=cls.GRID_COLOR, labelcolor=cls.TEXT_COLOR, loc="upper left")

        # Volume
        vols = df.get("volume", pd.Series(0, index=df.index))
        colors = [cls.ACCENT_GREEN if c >= o else cls.ACCENT_RED for c, o in zip(closes, df.get("open", closes))]
        ax2.bar(dates, vols, color=colors, alpha=0.7, width=1.0)
        cls._apply_theme(ax2, "", "", "Volume")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        fig.tight_layout()
        fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path

    @classmethod
    def plot_equity_curve(
        cls,
        strategy_curve: pd.Series,
        benchmark_curve: pd.Series,
        title: str,
        output_path: str,
        source_label: str = "Simulation",
        retrieval_time: str = ""
    ) -> str:
        """Renders backtest equity curve comparison vs benchmark with drawdown pane."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(16, 9), dpi=150,
            facecolor=cls.DARK_BG,
            gridspec_kw={"height_ratios": [3, 1]}
        )

        dates = strategy_curve.index
        ax1.plot(dates, strategy_curve, label="Strategy (Net of Fees)", color=cls.ACCENT_GREEN, linewidth=2.0)
        if benchmark_curve is not None and not benchmark_curve.empty:
            ax1.plot(benchmark_curve.index, benchmark_curve, label="Benchmark", color=cls.ACCENT_CYAN, linewidth=1.5, linestyle="--")

        sub = f"Execution: Open t+1 (Look-Ahead Bias Protected) | Source: {source_label} | Retrieved: {retrieval_time}"
        cls._apply_theme(ax1, title, sub, "Growth of $1.00")
        ax1.legend(facecolor=cls.PANEL_BG, edgecolor=cls.GRID_COLOR, labelcolor=cls.TEXT_COLOR, loc="upper left")

        # Drawdowns
        cummax = strategy_curve.cummax()
        dd = (strategy_curve - cummax) / cummax
        ax2.fill_between(dates, dd * 100, 0, color=cls.ACCENT_RED, alpha=0.4)
        ax2.plot(dates, dd * 100, color=cls.ACCENT_RED, linewidth=1.0)
        cls._apply_theme(ax2, "", "", "Drawdown (%)")

        fig.tight_layout()
        fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path

    @classmethod
    def plot_correlation_heatmap(
        cls,
        corr_matrix: pd.DataFrame,
        output_path: str,
        source_label: str = "Yahoo Finance",
        retrieval_time: str = ""
    ) -> str:
        """Renders correlation matrix heatmap."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 8), dpi=150, facecolor=cls.DARK_BG)
        ax.set_facecolor(cls.PANEL_BG)

        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="vlag",
            vmin=-1,
            vmax=1,
            cbar=True,
            ax=ax,
            cbar_kws={"label": "Correlation Coefficient"}
        )
        cls._apply_theme(ax, "Asset Correlation Heatmap", f"Source: {source_label} | Retrieved: {retrieval_time}")
        fig.tight_layout()
        fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path
