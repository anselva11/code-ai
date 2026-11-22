"""Pipeline stage progress widget for AXIOM TUI.
Visualizes execution stages: [Rencana] > [Analisa] > [Critic] > [Laporan]
with real-time running timer and stage spinners.
"""
import time
from typing import Dict
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

STAGES = ["Rencana", "Analisa", "Critic", "Laporan"]
SPINNERS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

class PipelineBar(Widget):
    DEFAULT_CSS = """
    PipelineBar {
        height: 1;
        background: $surface-darken-1;
        color: $text;
        padding: 0 1;
    }
    """
    spinner_idx = reactive(0)
    elapsed_seconds = reactive(0)
    is_active = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stage_states: Dict[str, str] = {s: "menunggu" for s in STAGES}
        self.start_time: float = 0.0
        self._timer = None

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        if self.is_active:
            self.spinner_idx = (self.spinner_idx + 1) % len(SPINNERS)
            self.elapsed_seconds = int(time.time() - self.start_time)
            self.refresh()

    def start_pipeline(self) -> None:
        self.stage_states = {s: "menunggu" for s in STAGES}
        self.start_time = time.time()
        self.elapsed_seconds = 0
        self.is_active = True
        self.refresh()

    def set_stage_status(self, stage: str, status: str) -> None:
        """status: menunggu | berjalan | selesai | gagal"""
        if stage in self.stage_states:
            self.stage_states[stage] = status
            self.refresh()

    def finish_pipeline(self, success: bool = True) -> None:
        self.is_active = False
        self.refresh()

    def reset_pipeline(self) -> None:
        self.is_active = False
        self.elapsed_seconds = 0
        self.stage_states = {s: "menunggu" for s in STAGES}
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append("PIPELINE: ", style="bold cyan")

        for idx, stage in enumerate(STAGES):
            st = self.stage_states.get(stage, "menunggu")
            if st == "menunggu":
                t.append(f"[{stage}]", style="dim")
            elif st == "berjalan":
                spin = SPINNERS[self.spinner_idx]
                t.append(f"[{spin} {stage}]", style="bold yellow on dark_blue")
            elif st == "selesai":
                t.append(f"[✓ {stage}]", style="bold green")
            elif st == "gagal":
                t.append(f"[✗ {stage}]", style="bold red")

            if idx < len(STAGES) - 1:
                t.append(" > ", style="dim white")

        # Timer format MM:SS
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        t.append(f"   {mins:02d}:{secs:02d}", style="bold white on black" if self.is_active else "dim")
        return t
