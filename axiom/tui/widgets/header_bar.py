"""Header widget for AXIOM TUI.
Displays system brand, active mode, audience, model, and engine status.
"""
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

class HeaderBar(Widget):
    DEFAULT_CSS = """
    HeaderBar {
        dock: top;
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 1;
    }
    """
    mode = reactive("quant")
    audience = reactive("analis")
    model_name = reactive("claude-3.5-sonnet")
    status_text = reactive("Siap")
    is_running = reactive(False)

    def render(self) -> Text:
        t = Text()
        t.append(" AXIOM ", style="bold white on blue")
        t.append("  [mode: ", style="dim")
        t.append(f"{self.mode}", style="bold cyan")
        t.append("]  [audiens: ", style="dim")
        t.append(f"{self.audience}", style="bold magenta")
        t.append("]  [model: ", style="dim")
        t.append(f"{self.model_name}", style="bold yellow")
        t.append("]  ", style="dim")

        if self.is_running:
            t.append("● RUNNING", style="bold green")
        else:
            t.append(f"● {self.status_text.upper()}", style="dim green")
        return t
