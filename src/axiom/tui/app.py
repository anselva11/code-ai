"""Main Textual Application for AXIOM TUI.
Strictly decoupled from execution engines: interacts solely via AxiomBackend Protocol.
"""
import os
import sys
from typing import Optional
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Static

from axiom.tui.backend import AxiomBackend, RunSummary, RunDetail
from axiom.tui.events import (
    StageStarted, StageFinished, PlanReady, ToolCall, ToolResult,
    VerdictReady, ReportReady, RunFinished, ErrorEvent
)
from axiom.tui.widgets.header_bar import HeaderBar
from axiom.tui.widgets.pipeline_bar import PipelineBar
from axiom.tui.widgets.sidebar_runs import SidebarRuns
from axiom.tui.widgets.sidebar_data import SidebarData
from axiom.tui.widgets.tabs_view import TabsView
from axiom.tui.widgets.question_input import QuestionInput
from axiom.tui.widgets.empty_state import EmptyState

from axiom.tui.screens.plan_modal import PlanModal
from axiom.tui.screens.command_palette import CommandPaletteModal
from axiom.tui.screens.help_modal import HelpModal
from axiom.tui.screens.error_modal import ErrorModal

class AxiomTUIApp(App[None]):
    TITLE = "AXIOM - AI Agent Quant & Research Finance"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("f1", "help", "Bantuan", show=True),
        Binding("f2", "toggle_mode", "Simple/Pro", show=True),
        Binding("ctrl+p", "command_palette", "Perintah", show=True),
        Binding("ctrl+c", "cancel_run", "Batal", show=True),
        Binding("ctrl+q", "quit", "Keluar", show=True),
        Binding("ctrl+y", "copy_report", "Salin", show=False),
        Binding("ctrl+s", "save_report", "Simpan", show=False),
    ]

    def __init__(self, backend: AxiomBackend, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend
        self.research_mode: str = "quant"
        self.target_audience: str = "analis"
        self.is_pro_mode: bool = True
        self.active_question: str = ""
        self._is_running: bool = False

    def compose(self) -> ComposeResult:
        yield HeaderBar(id="header-bar")
        with Horizontal(id="main-layout"):
            with Vertical(id="sidebar-container"):
                yield SidebarRuns(id="sidebar-runs")
                yield SidebarData(id="sidebar-data")

            with Vertical(id="content-container"):
                with Horizontal(id="convo-log-area"):
                    yield Label("Pertanyaan: [Belum ada]", id="convo-log-label")
                yield EmptyState(id="empty-state-banner")
                yield TabsView(id="tabs-view")

        with Vertical(id="bottom-controls"):
            yield PipelineBar(id="pipeline-bar")
            yield QuestionInput(id="question-input")
            yield Static(
                "ctrl+p perintah | F1 bantuan | F2 mode pro/simple | ctrl+c batal | ctrl+q keluar",
                id="keybindings-bar"
            )

    def on_mount(self) -> None:
        header = self.query_one(HeaderBar)
        header.mode = self.research_mode
        header.audience = self.target_audience

        # Load historical runs
        runs = self.backend.list_runs()
        self.query_one(SidebarRuns).update_runs(runs)

        # Focus question input
        self.query_one("#axiom-question-input").focus()

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_toggle_mode(self) -> None:
        self.is_pro_mode = not self.is_pro_mode
        tabs = self.query_one(TabsView)
        tabs.toggle_mode(self.is_pro_mode)
        mode_str = "PRO (Semua Tab)" if self.is_pro_mode else "SIMPLE (Laporan Saja)"
        self.notify(f"Mode tampilan diubah ke: {mode_str}")

    def action_command_palette(self) -> None:
        def on_palette_closed(result: Optional[dict]) -> None:
            if not result:
                return
            header = self.query_one(HeaderBar)
            if "mode" in result:
                self.research_mode = result["mode"]
                header.mode = self.research_mode
                self.notify(f"Mode riset: {self.research_mode}")
            elif "audience" in result:
                self.target_audience = result["audience"]
                header.audience = self.target_audience
                self.notify(f"Audiens laporan: {self.target_audience}")
            elif "theme" in result:
                new_theme = result["theme"]
                self.theme = "textual-dark" if new_theme == "dark" else "textual-light"
                self.notify(f"Tema tampilan: {new_theme}")

        self.push_screen(CommandPaletteModal(), on_palette_closed)

    def action_cancel_run(self) -> None:
        if self._is_running:
            self.backend.cancel()
            self.notify("Membatalkan eksekusi analisa...", severity="warning")

    def action_copy_report(self) -> None:
        tabs = self.query_one(TabsView)
        success = tabs.copy_report_to_clipboard()
        if success:
            self.notify("Laporan disalin ke clipboard.")
        else:
            self.notify("Belum ada laporan untuk disalin.", severity="warning")

    def action_save_report(self) -> None:
        tabs = self.query_one(TabsView)
        saved_path = tabs.save_report_to_file()
        if saved_path:
            self.notify(f"Laporan disimpan di: {os.path.basename(saved_path)}")
        else:
            self.notify("Belum ada laporan untuk disimpan.", severity="warning")

    def on_empty_state_question_chosen(self, event: EmptyState.QuestionChosen) -> None:
        q_input = self.query_one(QuestionInput)
        q_input.set_text(event.question)

    def on_sidebar_runs_run_selected(self, event: SidebarRuns.RunSelected) -> None:
        try:
            detail = self.backend.load_run(event.run_id)
            self._display_run_detail(detail)
            self.notify(f"Memuat run: {event.run_id}")
        except Exception as e:
            self.push_screen(ErrorModal(
                message=f"Gagal memuat arsip run: {e}",
                hint="Pastikan berkas run_meta.json dan report.md lengkap di folder runs/."
            ))

    def _display_run_detail(self, detail: RunDetail) -> None:
        self.query_one("#empty-state-banner").display = False
        convo_label = self.query_one("#convo-log-label", Label)
        convo_label.update(f"Pertanyaan: {detail.question}")

        tabs = self.query_one(TabsView)
        tabs.clear_all()
        tabs.set_plan(detail.plan, summary=f"Rencana untuk: {detail.question}")

        for tc in detail.tool_calls:
            tabs.add_tool_call(tc.get("step", 1), tc.get("agent", "Agent"), tc.get("code", ""))
            tabs.add_tool_result(tc.get("step", 1), tc.get("output", ""))

        tabs.set_critic_verdict(detail.verdict, detail.critic_findings)
        tabs.set_report(detail.report_markdown, charts=detail.chart_files, run_id=detail.id)

    def on_question_input_submitted(self, event: QuestionInput.Submitted) -> None:
        if self._is_running:
            self.notify("Sedang ada analisa yang berjalan. Harap tunggu atau tekan Ctrl+C.", severity="warning")
            return

        self.start_analysis(event.question)

    def start_analysis(self, question: str) -> None:
        self.active_question = question
        self._is_running = True

        # UI updates
        self.query_one("#empty-state-banner").display = False
        convo_label = self.query_one("#convo-log-label", Label)
        convo_label.update(f"Pertanyaan: {question}")

        header = self.query_one(HeaderBar)
        header.is_running = True
        header.status_text = "Memulai"

        pipeline = self.query_one(PipelineBar)
        pipeline.start_pipeline()

        tabs = self.query_one(TabsView)
        tabs.clear_all()

        # Run async worker
        self.run_worker(self._execute_pipeline(question), exclusive=True)

    async def _execute_pipeline(self, question: str) -> None:
        header = self.query_one(HeaderBar)
        pipeline = self.query_one(PipelineBar)
        tabs = self.query_one(TabsView)

        try:
            async for event in self.backend.run(question, mode=self.research_mode, audience=self.target_audience):
                ev_type = type(event).__name__

                if ev_type == "StageStarted":
                    pipeline.set_stage_status(event.stage, "berjalan")
                    header.status_text = f"Tahap: {event.stage}"

                elif ev_type == "StageFinished":
                    pipeline.set_stage_status(event.stage, "selesai")

                elif ev_type == "PlanReady":
                    tabs.set_plan(event.plan, event.summary)
                    # Open Plan Modal
                    def handle_plan_modal(result: tuple[bool, Optional[str]]) -> None:
                        approved, edited_question = result
                        self.backend.approve_plan(approved, edited_question)

                    self.push_screen(
                        PlanModal(event.plan, event.summary, self.active_question),
                        handle_plan_modal
                    )

                elif ev_type == "ToolCall":
                    tabs.add_tool_call(event.step, event.agent, event.code)

                elif ev_type == "ToolResult":
                    tabs.add_tool_result(event.step, event.output, event.error)

                elif ev_type == "VerdictReady":
                    tabs.set_critic_verdict(event.verdict, event.findings)

                elif ev_type == "ReportReady":
                    tabs.set_report(event.markdown, charts=[], run_id="latest")

                elif ev_type == "ErrorEvent":
                    self.push_screen(ErrorModal(event.message, event.hint))

                elif ev_type == "RunFinished":
                    self._is_running = False
                    header.is_running = False
                    header.status_text = "Selesai" if event.success else "Gagal"
                    pipeline.finish_pipeline(event.success)

                    # Refresh runs list in sidebar
                    runs = self.backend.list_runs()
                    self.query_one(SidebarRuns).update_runs(runs)

        except Exception as e:
            self._is_running = False
            header.is_running = False
            header.status_text = "Error"
            pipeline.finish_pipeline(False)
            self.push_screen(ErrorModal(
                message=f"Kesalahan tidak terduga pada backend: {e}",
                hint="Periksa koneksi sistem atau gunakan mode mock dengan: python -m axiom tui --mock"
            ))

def run_tui(use_mock: bool = True, backend: Optional[AxiomBackend] = None) -> None:
    if backend is None:
        from axiom.tui.mock import MockBackend
        backend = MockBackend()

    app = AxiomTUIApp(backend=backend)
    app.run()
