"""Sidebar widget displaying historical runs from runs/ directory."""
from textual.widget import Widget
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option
from textual.message import Message
from typing import List
from rich.text import Text
from axiom.tui.backend import RunSummary

class SidebarRuns(Widget):
    DEFAULT_CSS = """
    SidebarRuns {
        height: 1fr;
        border-bottom: solid $surface-lighten-2;
    }
    SidebarRuns Label {
        background: $primary-darken-2;
        color: $text;
        text-style: bold;
        padding: 0 1;
        width: 100%;
    }
    SidebarRuns OptionList {
        height: 1fr;
        scrollbar-size-vertical: 1;
    }
    """

    class RunSelected(Message):
        """Emitted when a user selects a run to inspect."""
        def __init__(self, run_id: str):
            super().__init__()
            self.run_id = run_id

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runs: List[RunSummary] = []

    def compose(self):
        yield Label("RIWAYAT RUN (Enter buka)")
        yield OptionList(id="runs-option-list")

    def update_runs(self, runs: List[RunSummary]) -> None:
        self.runs = runs
        option_list = self.query_one("#runs-option-list", OptionList)
        option_list.clear_options()

        if not runs:
            option_list.add_option(Option("[dim]Belum ada run tersimpan[/dim]", id="none", disabled=True))
            return

        for r in runs:
            text = Text()
            # Verdict badge
            if "LULUS DENGAN CATATAN" in r.verdict:
                text.append("[!] ", style="bold yellow")
            elif "LULUS" in r.verdict:
                text.append("[✓] ", style="bold green")
            elif "GAGAL" in r.verdict:
                text.append("[✗] ", style="bold red")
            else:
                text.append("[?] ", style="dim")

            text.append(f"{r.id}\n", style="bold")
            # Snippet of question
            snippet = r.question[:30] + ("..." if len(r.question) > 30 else "")
            text.append(f"  {snippet}", style="dim")
            option_list.add_option(Option(text, id=r.id))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_id and event.option_id != "none":
            self.post_message(self.RunSelected(str(event.option_id)))
