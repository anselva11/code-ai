"""Error modal screen displaying user-friendly diagnostics and actionable suggestions."""
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Static
from textual.containers import Vertical, Horizontal
from rich.text import Text

class ErrorModal(ModalScreen[None]):
    DEFAULT_CSS = """
    ErrorModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #error-dialog {
        width: 70;
        max-width: 90%;
        height: auto;
        background: $surface;
        border: thick $error;
        padding: 1 2;
    }
    #error-dialog Label.title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    #error-hint-box {
        background: $surface-lighten-1;
        border-left: thick $warning;
        padding: 1;
        margin-top: 1;
        margin-bottom: 1;
    }
    #error-btn-bar {
        align-horizontal: right;
    }
    """

    def __init__(self, message: str, hint: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.hint = hint

    def compose(self):
        with Vertical(id="error-dialog"):
            yield Label("⚠️ Kendala Eksekusi", classes="title")
            yield Label(self.message, id="error-message-label")

            with Vertical(id="error-hint-box"):
                t = Text()
                t.append("Saran Langkah Perbaikan:\n", style="bold yellow")
                t.append(self.hint, style="italic")
                yield Static(t)

            with Horizontal(id="error-btn-bar"):
                yield Button("Mengerti (Esc)", id="btn-close-error", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
