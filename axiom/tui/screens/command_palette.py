"""Command Palette modal (Ctrl+P) for fast settings without restart."""
from typing import Dict, Any, Optional
from textual.screen import ModalScreen
from textual.widgets import Label, Button, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal

OPTIONS = [
    ("mode:quant", "Mode: Quant (Faktor, Statistik & Valuasi)", "mode", "quant"),
    ("mode:backtest", "Mode: Backtest (Walk-forward & Eksekusi Portofolio)", "mode", "backtest"),
    ("mode:risk", "Mode: Risk (VaR, Stress Test & Sensitivitas Rezim)", "mode", "risk"),
    ("aud:pemula", "Audiens: Pemula (Penjelasan istilah ringkas & rekomendasi awam)", "audience", "pemula"),
    ("aud:analis", "Audiens: Analis (Metrik statistik lengkap, t-stat, dan p-value)", "audience", "analis"),
    ("aud:manajemen", "Audiens: Manajemen (Ringkasan eksekutif, tabel komparatif & risiko)", "audience", "manajemen"),
    ("theme:dark", "Tema: Dark Mode (Gelap kontras tinggi)", "theme", "dark"),
    ("theme:light", "Tema: Light Mode (Terang)", "theme", "light"),
]

class CommandPaletteModal(ModalScreen[Optional[Dict[str, str]]]):
    DEFAULT_CSS = """
    CommandPaletteModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #palette-dialog {
        width: 75;
        max-width: 90%;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    #palette-dialog Label.title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #palette-options {
        height: 12;
        margin-bottom: 1;
    }
    #palette-btn-bar {
        align-horizontal: right;
    }
    """

    def compose(self):
        with Vertical(id="palette-dialog"):
            yield Label("AXIOM Command Palette (Ctrl+P)", classes="title")
            yield Label("Pilih pengaturan cepat (Enter untuk menerapkan):")
            yield OptionList(
                *[Option(label, id=opt_id) for opt_id, label, _, _ in OPTIONS],
                id="palette-options"
            )
            with Horizontal(id="palette-btn-bar"):
                yield Button("Tutup (Esc)", id="btn-close", variant="default")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        sel_id = event.option_id
        for opt_id, _, key, val in OPTIONS:
            if opt_id == sel_id:
                self.dismiss({key: val})
                return
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
