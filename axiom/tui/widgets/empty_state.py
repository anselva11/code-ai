"""Empty state widget shown on startup with sample questions."""
from textual.widget import Widget
from textual.widgets import Label, Button
from textual.containers import Vertical, Horizontal
from textual.message import Message

SAMPLE_QUESTIONS = [
    "Bandingkan momentum 12-1 bulan vs buy-and-hold di saham LQ45 5 tahun terakhir.",
    "Uji korelasi sektor perbankan vs perubahan BI Rate selama siklus pengetatan moneter.",
    "Hitung Value-at-Risk (VaR 95% & 99%) portofolio 5 saham big cap Indonesia dengan historical simulation."
]

class EmptyState(Widget):
    DEFAULT_CSS = """
    EmptyState {
        height: auto;
        padding: 1 2;
        background: $surface;
        border: round $primary;
        margin: 1;
    }
    EmptyState Label.title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    EmptyState Label.desc {
        color: $text;
        margin-bottom: 1;
    }
    EmptyState Button {
        margin: 0 0 1 0;
        width: 100%;
        text-align: left;
    }
    """

    class QuestionChosen(Message):
        """Emitted when user picks one of the sample questions."""
        def __init__(self, question: str):
            super().__init__()
            self.question = question

    def compose(self):
        with Vertical():
            yield Label("Selamat datang di AXIOM Quantitative Research", classes="title")
            yield Label(
                "Sistem agen kuantitatif berbasis audit: semua angka berasal dari eksekusi kode deterministik, "
                "dilarang halusinasi, dan wajib lolos audit Critic sebelum disajikan.\n"
                "Pilih salah satu contoh pertanyaan di bawah atau ketik langsung di kolom input:",
                classes="desc"
            )
            for idx, q in enumerate(SAMPLE_QUESTIONS, start=1):
                yield Button(f"{idx}. {q}", id=f"sample-btn-{idx}", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "sample-btn-1":
            self.post_message(self.QuestionChosen(SAMPLE_QUESTIONS[0]))
        elif btn_id == "sample-btn-2":
            self.post_message(self.QuestionChosen(SAMPLE_QUESTIONS[1]))
        elif btn_id == "sample-btn-3":
            self.post_message(self.QuestionChosen(SAMPLE_QUESTIONS[2]))
