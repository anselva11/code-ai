"""AXIOM AI AGENTS — Institutional CLI powered by Typer and Rich."""
import sys
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import datetime
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from axiom import __app_name__, __tagline__, __version__
from axiom.orchestrator import Orchestrator
from axiom.data.providers.news import NewsProvider

app = typer.Typer(
    name="axiom",
    help="AXIOM AI AGENTS — Autonomous Financial Intelligence & Quantitative Research System",
    no_args_is_help=False,
    invoke_without_command=True
)

quant_app = typer.Typer(help="Analisis kuantitatif dan simulasi backtest")
app.add_typer(quant_app, name="quant")

portfolio_app = typer.Typer(help="Analisis risiko dan alokasi portofolio multi-aset")
app.add_typer(portfolio_app, name="portfolio")

console = Console()

def print_banner():
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    console.print(Panel(
        f"[bold white]{__app_name__}[/bold white] [dim]v{__version__}[/dim]\n"
        f"[bold cyan]{__tagline__}[/bold cyan]\n"
        f"[dim]Waktu Sistem: {now_utc} | Environment: Production | Execution: Deterministic[/dim]",
        border_style="blue",
        padding=(0, 2)
    ))

def print_cli_error(e: Exception):
    console.print(Panel(
        f"[bold red]Perhatian:[/bold red] {str(e)}\n\n"
        f"[dim]Saran: Periksa koneksi internet, pastikan format simbol valid (contoh: AAPL, NVDA, BTC-USD, SPY), atau pilih opsi waktu yang tersedia di cache.[/dim]",
        title="[bold yellow]AXIOM Notification[/bold yellow]",
        border_style="yellow"
    ))

@app.callback()
def main(ctx: typer.Context):
    """Callback triggered before commands, or when bare 'axiom' is invoked."""
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("[bold yellow]Mode Interaktif Riset Finansial[/bold yellow] (Ketik 'keluar' atau 'exit' untuk selesai)\n")
        orchestrator = Orchestrator(console=console)

        while True:
            try:
                query = console.input("[bold green]axiom > [/bold green]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Sesi diakhiri.[/dim]")
                break

            if not query:
                continue
            if query.lower() in ("exit", "keluar", "quit", "q"):
                console.print("[dim]Sampai jumpa.[/dim]")
                break

            # Natural language planner & router
            console.print(f"\n[bold cyan]>[/bold cyan] Memproses pertanyaan: [italic]{query}[/italic]")
            if "backtest" in query.lower() or "strategi" in query.lower():
                parts = query.split()
                sym = "SPY"
                for p in parts:
                    if p.isupper() and len(p) <= 5:
                        sym = p
                report_dir = orchestrator.run_backtest(symbol=sym, strategy="momentum", period="5y")
            elif "makro" in query.lower() or "macro" in query.lower() or "suku bunga" in query.lower():
                report_dir = orchestrator.run_macro(region="US")
            elif "news" in query.lower() or "berita" in query.lower():
                report_dir = orchestrator.run_macro(region="US")
            else:
                # Default to research / market
                sym = "AAPL"
                for w in query.replace("?", "").replace(",", "").split():
                    if w.isupper() and 2 <= len(w) <= 5:
                        sym = w
                        break
                report_dir = orchestrator.run_market(sym)

            console.print(f"[bold green]✓ Selesai.[/bold green] Laporan disimpan di: [bold underline]{report_dir}[/bold underline]\n")

@app.command("status")
def status():
    """Tampilkan status identitas sistem, konfigurasi, cache, dan provider."""
    print_banner()
    t = Table(title="Status Layanan & Komponen AXIOM", border_style="blue")
    t.add_column("Komponen", style="bold")
    t.add_column("Status", style="green")
    t.add_column("Provider / Engine", style="cyan")
    t.add_column("Freshness Policy")

    t.add_row("Market Data Engine", "AKTIF", "Yahoo Finance (Community / Delayed)", "DELAYED (15m) / EOD")
    t.add_row("Crypto Data Feed", "AKTIF", "Yahoo Crypto / Exchange Public", "DELAYED (1m - 15m)")
    t.add_row("Macroeconomic Feed", "AKTIF", "Treasuries / DXY / Commodities", "DELAYED / END-OF-DAY")
    t.add_row("News & Media Retrieval", "AKTIF", "RSS Verified Financial Feeds", "PUBLICATION TIMESTAMP")
    t.add_row("Deterministic Quant Core", "AKTIF", "Python 3.13 / NumPy / SciPy", "EXACT / REPRODUCIBLE")
    t.add_row("Skeptic / Verification", "AKTIF", "Rule-based Audit Agent", "ZERO LOOK-AHEAD BIAS (t+1)")

    console.print(t)
    console.print("[dim]Direktori Cache: data/cache/ | Direktori Laporan: reports/[/dim]\n")

@app.command("sources")
def sources():
    """Tampilkan daftar sumber data internet, lisensi, dan status atribusi."""
    print_banner()
    t = Table(title="Daftar Sumber Data & Provider AXIOM", border_style="blue")
    t.add_column("Provider", style="bold")
    t.add_column("Cakupan Aset", style="cyan")
    t.add_column("Kebutuhan API Key", style="yellow")
    t.add_column("Freshness / SLA", style="magenta")
    t.add_column("Atribusi / Lisensi")

    t.add_row("Yahoo Finance", "Saham, ETF, Crypto, Valuta, Komoditas", "Gratis / Tanpa Key", "DELAYED / EOD", "Sumber Komunitas Tidak Resmi")
    t.add_row("FRED St. Louis Fed", "Indikator Makro, Suku Bunga, Inflasi AS", "Opsional (Gratis)", "END-OF-DAY", "Domain Publik Pemerintah AS")
    t.add_row("SEC EDGAR / XBRL", "Laporan Keuangan Perusahaan AS (10-K, 10-Q)", "Gratis / User-Agent", "PUBLICATION DATE", "Dokumen Primer Regulator AS")
    t.add_row("Public Exchange APIs", "Aset Kripto (Spot, Volume 24j)", "Gratis / Tanpa Key", "REAL-TIME / DELAYED", "Endpoint Publik Bursa Kripto")
    t.add_row("Verified News RSS", "Berita Finansial & Kebijakan Bank Sentral", "Gratis / Tanpa Key", "PUBLICATION DATE", "Media Finansial Terakreditasi")

    console.print(t)
    console.print("[dim]Aturan Kepatuhan: AXIOM tidak pernah melabeli feed komunitas sebagai real-time resmi.[/dim]\n")

@app.command("market")
def market(
    symbol: str = typer.Argument(..., help="Simbol ticker aset (misal: AAPL, BTC-USD, SPY)"),
    asset: str = typer.Option("equity", "--asset", "-a", help="Tipe aset: equity | crypto | commodity | fx"),
    period: str = typer.Option("1y", "--period", "-p", help="Horizon waktu (1mo, 6mo, 1y, 2y, 5y)")
):
    """Ambil data pasar, hitung volatilitas & teknikal, dan buat laporan bertanggal."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    try:
        report_dir = orchestrator.run_market(symbol=symbol, asset_type=asset, period=period)
        console.print(f"\n[bold green]✓ Analisis pasar selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@app.command("research")
def research(
    target: str = typer.Argument(..., help="Nama atau ticker perusahaan / aset (misal: NVIDIA, NVDA, AAPL)"),
    type_: str = typer.Option("company", "--type", "-t", help="Tipe target riset (company / crypto / asset)")
):
    """Lakukan riset fundamental mendalam, valuasi, marjin, dan kesehatan neraca."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    sym = "NVDA" if "NVIDIA" in target.upper() else target.upper()
    try:
        report_dir = orchestrator.run_research(target=sym, target_type=type_)
        console.print(f"\n[bold green]✓ Riset perusahaan selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@app.command("macro")
def macro(
    region: str = typer.Option("US", "--region", "-r", help="Kawasan analisis makroekonomi (US, GLOBAL)")
):
    """Analisis lingkungan makroekonomi, kurva imbal hasil (yield curve), dan DXY."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    try:
        report_dir = orchestrator.run_macro(region=region)
        console.print(f"\n[bold green]✓ Analisis makro selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@app.command("news")
def news(
    query: str = typer.Argument(..., help="Topik berita atau katalis pasar yang dicari")
):
    """Ambil dan verifikasi berita finansial terkini serta publikasi bank sentral."""
    print_banner()
    console.print(f"[bold cyan]>[/bold cyan] Mencari berita pasar untuk topik: [italic]'{query}'[/italic]...\n")
    provider = NewsProvider()
    articles = provider.get_news(query=query, limit=10)

    if not articles:
        console.print("[yellow]Tidak ditemukan artikel terkini untuk kueri tersebut.[/yellow]")
        return

    table = Table(title=f"Berita Finansial Terkini: '{query}'", border_style="blue")
    table.add_column("Sumber Media", style="cyan", width=22)
    table.add_column("Waktu Publikasi", style="dim", width=24)
    table.add_column("Judul Berita", style="bold")

    for a in articles:
        table.add_row(a.source_name, a.published_date[:22], a.title)

    console.print(table)
    console.print(f"\n[dim]Ditemukan {len(articles)} artikel primer/media terakreditasi.[/dim]")

@quant_app.command("analyze")
def quant_analyze(
    symbol: str = typer.Argument(..., help="Simbol aset yang dianalisis"),
    period: str = typer.Option("5y", "--period", "-p", help="Horizon observasi (1y, 2y, 5y, 10y)")
):
    """Analisis kuantitatif mendalam: CAGR, Sharpe, Sortino, Calmar, dan Drawdown."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    try:
        report_dir = orchestrator.run_market(symbol=symbol, period=period)
        console.print(f"\n[bold green]✓ Analisis kuantitatif selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@quant_app.command("backtest")
def quant_backtest(
    strategy: str = typer.Option("momentum", "--strategy", "-s", help="Strategi: momentum | crossover | mean_reversion | buy_and_hold"),
    symbol: str = typer.Option("SPY", "--symbol", help="Simbol aset yang disimulasikan"),
    period: str = typer.Option("10y", "--period", "-p", help="Periode backtest historis")
):
    """Jalankan simulasi backtest dengan eksekusi timing t+1 untuk mencegah look-ahead bias."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    try:
        report_dir = orchestrator.run_backtest(symbol=symbol, strategy=strategy, period=period)
        console.print(f"\n[bold green]✓ Simulasi backtest selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@portfolio_app.command("analyze")
def portfolio_analyze(
    csv_file: str = typer.Argument(..., help="Path ke berkas CSV portofolio (kolom minimal: ticker, quantity atau portfolio_weight)")
):
    """Analisis konsentrasi HHI, matriks korelasi, dan sensitivitas portofolio."""
    print_banner()
    orchestrator = Orchestrator(console=console)
    try:
        report_dir = orchestrator.run_portfolio(csv_filepath=csv_file)
        console.print(f"\n[bold green]✓ Analisis portofolio selesai.[/bold green] Laporan tersimpan di:\n[bold underline]{report_dir}[/bold underline]")
    except Exception as e:
        print_cli_error(e)
        raise typer.Exit(code=1)

@app.command("report")
def report_latest(
    target: str = typer.Argument("latest", help="Target laporan (default: latest)")
):
    """Buka dan tampilkan ringkasan laporan analisis terbaru dari direktori reports/."""
    print_banner()
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        console.print("[yellow]Belum ada laporan di folder reports/.[/yellow]")
        return

    subdirs = [os.path.join(reports_dir, d) for d in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, d))]
    if not subdirs:
        console.print("[yellow]Folder reports/ kosong.[/yellow]")
        return

    latest_dir = sorted(subdirs)[-1]
    report_md_path = os.path.join(latest_dir, "report.md")

    if os.path.exists(report_md_path):
        console.print(f"[bold cyan]Menampilkan Laporan Terbaru:[/bold cyan] [underline]{latest_dir}[/underline]\n")
        with open(report_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        console.print(Markdown(content))
    else:
        console.print(f"[yellow]Berkas report.md tidak ditemukan di {latest_dir}.[/yellow]")

@app.command("tui")
def tui_command(
    mock: bool = typer.Option(False, "--mock", help="Jalankan dalam mode mock tanpa API key")
):
    """Buka antarmuka Terminal User Interface (TUI)."""
    from axiom.tui.app import run_tui
    run_tui(use_mock=mock)

if __name__ == "__main__":
    app()
