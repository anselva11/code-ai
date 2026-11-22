"""Automated tests for AXIOM TUI using Textual Pilot."""
import pytest
import asyncio
from axiom.tui.app import AxiomTUIApp
from axiom.tui.mock import MockBackend
from axiom.tui.screens.plan_modal import PlanModal
from axiom.tui.screens.command_palette import CommandPaletteModal
from axiom.tui.screens.help_modal import HelpModal
from axiom.tui.widgets.header_bar import HeaderBar
from axiom.tui.widgets.pipeline_bar import PipelineBar
from axiom.tui.widgets.tabs_view import TabsView
from axiom.tui.widgets.question_input import QuestionInput
from axiom.tui.widgets.empty_state import EmptyState
from axiom.tui.widgets.sidebar_runs import SidebarRuns
from textual.widgets import Input, Button, Markdown

def test_initial_layout():
    """Verify all primary components mount with expected initial state."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            # Check core widgets presence
            assert app.query_one(HeaderBar) is not None
            assert app.query_one(PipelineBar) is not None
            assert app.query_one(TabsView) is not None
            assert app.query_one(QuestionInput) is not None
            assert app.query_one(SidebarRuns) is not None
            assert app.query_one(EmptyState) is not None

            # Verify header initial values
            header = app.query_one(HeaderBar)
            assert header.mode == "quant"
            assert header.audience == "analis"
            assert not header.is_running
    asyncio.run(_test())

def test_simple_pro_mode_toggle():
    """Verify F2 toggles between Simple and Pro mode."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            tabs = app.query_one(TabsView)
            assert app.is_pro_mode is True

            # Press F2 to switch to Simple Mode
            await pilot.press("f2")
            await pilot.pause()
            assert app.is_pro_mode is False
            assert tabs.is_pro_mode is False

            # Press F2 again to switch back to Pro Mode
            await pilot.press("f2")
            await pilot.pause()
            assert app.is_pro_mode is True
            assert tabs.is_pro_mode is True
    asyncio.run(_test())

def test_help_modal():
    """Verify F1 opens HelpModal and Escape closes it."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            await pilot.press("f1")
            await pilot.pause()

            # Check HelpModal is active
            assert isinstance(app.screen, HelpModal)

            # Press escape to close
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, HelpModal)
    asyncio.run(_test())

def test_command_palette():
    """Verify Ctrl+P opens CommandPaletteModal and changes settings."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            await pilot.press("ctrl+p")
            await pilot.pause()

            assert isinstance(app.screen, CommandPaletteModal)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, CommandPaletteModal)
    asyncio.run(_test())

def test_empty_state_button():
    """Verify clicking empty state sample question populates the input."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            btn1 = app.query_one("#sample-btn-1", Button)
            await pilot.click(btn1)
            await pilot.pause()

            inp = app.query_one("#axiom-question-input", Input)
            assert "momentum 12-1" in inp.value.lower()
    asyncio.run(_test())

def test_load_historical_run():
    """Verify selecting a past run from sidebar loads details and report."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            sidebar = app.query_one(SidebarRuns)
            assert len(sidebar.runs) > 0
            run_id = sidebar.runs[0].id

            # Trigger run selection
            sidebar.post_message(SidebarRuns.RunSelected(run_id))
            await pilot.pause()

            # Check that empty state is hidden and report is loaded
            assert app.query_one("#empty-state-banner").display is False
            tabs = app.query_one(TabsView)
            assert "Laporan Riset" in tabs.current_report_md
    asyncio.run(_test())

def test_pipeline_end_to_end_approval():
    """Verify end-to-end question submission, plan approval, and verified report display."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            inp = app.query_one("#axiom-question-input", Input)
            inp.value = "Uji momentum 12-1m vs LQ45"
            await pilot.press("enter")
            await pilot.pause()

            # Plan modal should appear
            assert isinstance(app.screen, PlanModal)

            # Click approve button on PlanModal
            approve_btn = app.screen.query_one("#btn-approve", Button)
            await pilot.click(approve_btn)
            await pilot.pause()

            # Wait briefly for mock pipeline stages to run
            for _ in range(15):
                await pilot.pause(0.05)
                if not app._is_running:
                    break

            # Verify pipeline finished successfully
            assert not app._is_running
            header = app.query_one(HeaderBar)
            assert header.status_text == "Selesai"

            # Verify Report was generated and rendered
            tabs = app.query_one(TabsView)
            assert "Laporan Riset Kuantitatif AXIOM" in tabs.current_report_md
            md_text = app.query_one("#report-markdown", Markdown)
            assert md_text is not None
    asyncio.run(_test())

def test_pipeline_cancellation():
    """Verify plan cancellation stops execution cleanly without crash."""
    async def _test():
        backend = MockBackend(delay_factor=0.0)
        app = AxiomTUIApp(backend=backend)
        async with app.run_test() as pilot:
            inp = app.query_one("#axiom-question-input", Input)
            inp.value = "Tes pembatalan analisa"
            await pilot.press("enter")
            await pilot.pause()

            assert isinstance(app.screen, PlanModal)
            cancel_btn = app.screen.query_one("#btn-cancel", Button)
            await pilot.click(cancel_btn)
            await pilot.pause()

            # Wait for run to finish as failed/cancelled
            for _ in range(10):
                await pilot.pause(0.05)
                if not app._is_running:
                    break

            assert not app._is_running
    asyncio.run(_test())
