"""Question input widget with history buffer (Up/Down navigation)."""
from textual.widget import Widget
from textual.widgets import Input
from textual.message import Message
from textual import events
from typing import List

class QuestionInput(Widget):
    DEFAULT_CSS = """
    QuestionInput {
        height: 3;
        dock: bottom;
        background: $surface;
        padding: 0 1;
    }
    QuestionInput Input {
        border: tall $primary;
        height: 3;
        padding: 0 1;
    }
    """

    class Submitted(Message):
        """Emitted when user presses Enter on question input."""
        def __init__(self, question: str):
            super().__init__()
            self.question = question

    def __init__(self, placeholder: str = "Tulis pertanyaan riset quant (misal: 'Bandingkan momentum 12-1m vs IHSG')...", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.history: List[str] = []
        self.history_index: int = -1
        self._temp_input: str = ""

    def compose(self):
        yield Input(placeholder=self.placeholder, id="axiom-question-input")

    def set_text(self, text: str) -> None:
        inp = self.query_one("#axiom-question-input", Input)
        inp.value = text
        inp.cursor_position = len(text)
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if val:
            if not self.history or self.history[-1] != val:
                self.history.append(val)
            self.history_index = len(self.history)
            self._temp_input = ""
            event.input.value = ""
            self.post_message(self.Submitted(val))

    def on_key(self, event: events.Key) -> None:
        inp = self.query_one("#axiom-question-input", Input)
        if event.key == "up":
            if not self.history:
                return
            if self.history_index == -1 or self.history_index == len(self.history):
                self._temp_input = inp.value
                self.history_index = len(self.history) - 1
            elif self.history_index > 0:
                self.history_index -= 1

            if 0 <= self.history_index < len(self.history):
                inp.value = self.history[self.history_index]
                inp.cursor_position = len(inp.value)
            event.prevent_default()
            event.stop()

        elif event.key == "down":
            if not self.history or self.history_index == -1:
                return
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                inp.value = self.history[self.history_index]
                inp.cursor_position = len(inp.value)
            elif self.history_index == len(self.history) - 1:
                self.history_index = len(self.history)
                inp.value = self._temp_input
                inp.cursor_position = len(inp.value)
            event.prevent_default()
            event.stop()
