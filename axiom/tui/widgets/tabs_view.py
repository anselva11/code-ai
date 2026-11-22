"""TabsView widget holding Rencana, Kode, Output, Critic, and Laporan panes."""
import os
import sys
import subprocess
from typing import List, Dict, Any, Optional
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane, Markdown, Label, Button, RichLog, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel

class TabsView(Widget):
    DEFAULT_CSS = """
    TabsView {
        height: 1fr;
    }
    TabsView TabbedContent {
        height: 1fr;
    }
    TabsView TabPane {
        padding: 1;
        height: 1fr;
    }
    #actions-bar {
        height: auto;
        dock: top;
        padding-bottom: 1;
    }
    #actions-bar Button {
        margin-right: 1;
    }
    .verdict-lulus {
        background: darkgreen;
        color: white;
        text-style: bold;
        padding: 0 1;
        margin-bottom: 1;
    }
    .verdict-catatan {
        background: darkgoldenrod;
        color: black;
        text-style: bold;
        padding: 0 1;
        margin-bottom: 1;
    }
    .verdict-gagal {
        background: darkred;
        color: white;
        text-style: bold;
        padding: 0 1;
        margin-bottom: 1;
    }
    .finding-card {
        background: $surface;
        border: round $primary;
        padding: 1;
        margin-bottom: 1;
    }
    .plan-card {
        background: $surface;
        border-left: thick $accent;
        padding: 1;
        margin-bottom: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_report_md: str = ""
        self.current_charts: List[str] = []
        self.current_run_id: str = "latest"
        self.is_pro_mode: bool = True

    def compose(self):
        with TabbedContent(id="tabs-container"):
            with TabPane("Rencana", id="tab-rencana"):
                yield ScrollableContainer(id="rencana-container")

            with TabPane("Kode", id="tab-kode"):
                yield RichLog(id="kode-log", highlight=True, markup=True)

            with TabPane("Output", id="tab-output"):
                yield RichLog(id="output-log", highlight=True, markup=True)

            with TabPane("Critic", id="tab-critic"):
                yield ScrollableContainer(id="critic-container")

            with TabPane("Laporan", id="tab-laporan"):
                with Vertical():
                    with Horizontal(id="actions-bar"):
                        yield Button("📋 Salin (Ctrl+Y)", id="btn-copy-report", variant="default")
                        yield Button("💾 Simpan (Ctrl+S)", id="btn-save-report", variant="default")
                        yield Label("", id="report-save-status")
                    with Horizontal(id="chart-buttons-bar"):
                        yield Label("", id="chart-list-label")
                    yield Markdown("# Belum ada laporan\n\nKetik pertanyaan riset di bawah untuk memulai analisa.", id="report-markdown")

    def toggle_mode(self, is_pro: bool) -> None:
        """Toggles between Simple Mode (only Laporan) and Pro Mode (all tabs)."""
        self.is_pro_mode = is_pro
        tab_container = self.query_one("#tabs-container", TabbedContent)
        
        # When simple mode, force focus to Laporan
        if not is_pro:
            tab_container.active = "tab-laporan"
            self.query_one("#tab-rencana", TabPane).display = False
            self.query_one("#tab-kode", TabPane).display = False
            self.query_one("#tab-output", TabPane).display = False
            self.query_one("#tab-critic", TabPane).display = False
        else:
            self.query_one("#tab-rencana", TabPane).display = True
            self.query_one("#tab-kode", TabPane).display = True
            self.query_one("#tab-output", TabPane).display = True
            self.query_one("#tab-critic", TabPane).display = True

    def clear_all(self) -> None:
        """Resets all tab contents for a new run."""
        self.query_one("#rencana-container", ScrollableContainer).remove_children()
        self.query_one("#kode-log", RichLog).clear()
        self.query_one("#output-log", RichLog).clear()
        self.query_one("#critic-container", ScrollableContainer).remove_children()
        self.current_report_md = ""
        self.current_charts = []
        self.query_one("#report-markdown", Markdown).update("# Menganalisa...\n\nMohon tunggu, pipeline sedang berjalan.")
        self._update_chart_buttons([])

    def set_plan(self, plan: List[Dict[str, str]], summary: str = "") -> None:
        container = self.query_one("#rencana-container", ScrollableContainer)
        container.remove_children()

        if summary:
            t = Text(f"Ringkasan Rencana:\n{summary}\n", style="bold cyan")
            container.mount(Static(t))

        for step in plan:
            card_text = Text()
            card_text.append(f"Langkah {step.get('step', '?')}: ", style="bold magenta")
            card_text.append(f"[{step.get('agent', 'Orchestrator')}]\n", style="bold yellow")
            card_text.append(f"Tugas: ", style="bold")
            card_text.append(f"{step.get('task', '')}\n")
            card_text.append(f"Kriteria Berhasil: ", style="dim")
            card_text.append(f"{step.get('success_criteria', '')}", style="green")

            card = Static(card_text, classes="plan-card")
            container.mount(card)

        # Switch to rencana tab initially
        if self.is_pro_mode:
            self.query_one("#tabs-container", TabbedContent).active = "tab-rencana"

    def add_tool_call(self, step: int, agent: str, code: str) -> None:
        kode_log = self.query_one("#kode-log", RichLog)
        kode_log.write(f"\n[bold cyan]━━━ Langkah {step} : {agent} ━━━[/bold cyan]")
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True, word_wrap=True)
        kode_log.write(syntax)

        if self.is_pro_mode:
            self.query_one("#tabs-container", TabbedContent).active = "tab-kode"

    def add_tool_result(self, step: int, output: str, error: bool = False) -> None:
        output_log = self.query_one("#output-log", RichLog)
        status = "[bold red]FAILED[/bold red]" if error else "[bold green]PASSED[/bold green]"
        output_log.write(f"\n[bold]Langkah {step} Result ({status}):[/bold]")
        output_log.write(output)

    def set_critic_verdict(self, verdict: str, findings: List[Dict[str, Any]]) -> None:
        container = self.query_one("#critic-container", ScrollableContainer)
        container.remove_children()

        # Verdict Header
        v_class = "verdict-lulus"
        icon = "[✓]"
        if "CATATAN" in verdict:
            v_class = "verdict-catatan"
            icon = "[!]"
        elif "GAGAL" in verdict:
            v_class = "verdict-gagal"
            icon = "[✗]"

        banner = Label(f"  {icon} VERDICT CRITIC: {verdict.upper()}  ", classes=v_class)
        container.mount(banner)

        # Findings
        if not findings:
            container.mount(Static("[green]✓ Tidak ada temuan deviasi atau bias kritis. Analisa terverifikasi.[/green]"))
        else:
            container.mount(Label(f"Daftar Temuan Audit ({len(findings)} temuan):", classes="desc"))
            for idx, item in enumerate(findings, start=1):
                sev = item.get("severity", "Sedang")
                sev_color = "red" if sev.lower() == "tinggi" else ("yellow" if sev.lower() == "sedang" else "cyan")

                t = Text()
                t.append(f"{idx}. ", style="bold")
                t.append(f"[{sev.upper()}] ", style=f"bold {sev_color}")
                t.append(f"{item.get('finding', '')}\n")
                if "mitigation" in item:
                    t.append("   Tindakan Mitigasi: ", style="bold dim")
                    t.append(f"{item.get('mitigation')}", style="italic green")

                card = Static(t, classes="finding-card")
                container.mount(card)

    def set_report(self, markdown_text: str, charts: Optional[List[str]] = None, run_id: str = "latest") -> None:
        self.current_report_md = markdown_text
        self.current_charts = charts or []
        self.current_run_id = run_id

        md_widget = self.query_one("#report-markdown", Markdown)
        md_widget.update(markdown_text)

        self._update_chart_buttons(self.current_charts)
        self.query_one("#tabs-container", TabbedContent).active = "tab-laporan"

    def _update_chart_buttons(self, charts: List[str]) -> None:
        chart_bar = self.query_one("#chart-buttons-bar", Horizontal)
        chart_bar.remove_children()

        if charts:
            chart_bar.mount(Label("[bold]Grafik Run:[/bold] "))
            for chart_name in charts:
                btn = Button(f"🖼 {chart_name}", id=f"chart-btn-{chart_name}", variant="primary")
                chart_bar.mount(btn)

    def copy_report_to_clipboard(self) -> bool:
        if not self.current_report_md:
            return False
        try:
            self.app.copy_to_clipboard(self.current_report_md)
            lbl = self.query_one("#report-save-status", Label)
            lbl.update("[green]✓ Disalin ke clipboard![/green]")
            return True
        except Exception:
            return False

    def save_report_to_file(self) -> Optional[str]:
        if not self.current_report_md:
            return None
        filename = f"laporan_{self.current_run_id}.md"
        filepath = os.path.abspath(filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.current_report_md)
            lbl = self.query_one("#report-save-status", Label)
            lbl.update(f"[green]✓ Tersimpan: {filename}[/green]")
            return filepath
        except Exception as e:
            lbl = self.query_one("#report-save-status", Label)
            lbl.update(f"[red]Gagal simpan: {e}[/red]")
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-copy-report":
            self.copy_report_to_clipboard()
        elif btn_id == "btn-save-report":
            self.save_report_to_file()
        elif btn_id and btn_id.startswith("chart-btn-"):
            chart_filename = btn_id.replace("chart-btn-", "")
            self._open_chart_file(chart_filename)

    def _open_chart_file(self, filename: str) -> None:
        """Opens chart image with OS default viewer."""
        path = os.path.join("runs", self.current_run_id, filename)
        if not os.path.exists(path):
            path = filename
        if os.path.exists(path):
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", path])
                elif sys.platform == "win32":
                    os.startfile(path)
            except Exception:
                pass
