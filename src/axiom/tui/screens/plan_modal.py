"""Modal screen for Plan Review & Approval (Lanjutkan / Ubah / Batal)."""
from typing import List, Dict, Tuple, Optional
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer
from rich.text import Text

class PlanModal(ModalScreen[Tuple[bool, Optional[str]]]):
    DEFAULT_CSS = """
    PlanModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #plan-dialog {
        width: 80;
        max-width: 90%;
        height: auto;
        max-height: 85%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    #plan-dialog Label.title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #plan-steps-container {
        max-height: 12;
        border: solid $surface-lighten-2;
        padding: 1;
        margin-bottom: 1;
    }
    .modal-step-card {
        margin-bottom: 1;
    }
    #plan-button-bar {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    #plan-button-bar Button {
        margin-left: 1;
    }
    """

    def __init__(self, plan: List[Dict[str, str]], summary: str, current_question: str, **kwargs):
        super().__init__(**kwargs)
        self.plan = plan
        self.summary = summary
        self.current_question = current_question

    def compose(self):
        with Vertical(id="plan-dialog"):
            yield Label("Persetujuan Rencana Riset AXIOM", classes="title")
            yield Label(f"Ringkasan: {self.summary}", id="plan-summary-label")

            with ScrollableContainer(id="plan-steps-container"):
                for step in self.plan:
                    t = Text()
                    t.append(f"Langkah {step.get('step', '?')}: ", style="bold cyan")
                    t.append(f"[{step.get('agent', 'Agent')}] ", style="bold yellow")
                    t.append(f"{step.get('task', '')}\n")
                    t.append(f"  Target: {step.get('success_criteria', '')}", style="dim")
                    yield Static(t, classes="modal-step-card")

            yield Label("Edit Pertanyaan (jika ingin mengubah cakupan):")
            yield Input(value=self.current_question, id="input-edit-question")

            with Horizontal(id="plan-button-bar"):
                yield Button("Lanjutkan", id="btn-approve", variant="success")
                yield Button("Ubah & Jalankan", id="btn-edit-run", variant="primary")
                yield Button("Batal", id="btn-cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        edited_val = self.query_one("#input-edit-question", Input).value.strip()

        if btn_id == "btn-approve":
            self.dismiss((True, None))
        elif btn_id == "btn-edit-run":
            self.dismiss((True, edited_val if edited_val else None))
        elif btn_id == "btn-cancel":
            self.dismiss((False, None))

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss((False, None))
