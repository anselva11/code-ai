"""Help screen modal (F1) displaying shortcuts and sample research queries."""
from textual.screen import ModalScreen
from textual.widgets import Label, Button, DataTable, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer
from rich.text import Text

SHORTCUTS = [
    ("F1", "Bantuan & Panduan Keyboard"),
    ("F2", "Toggle Mode: Simple (ringkasan) <-> Pro (semua tab)"),
    ("Ctrl + P", "Command Palette: Ganti Mode, Audiens, & Tema"),
    ("Ctrl + C", "Batalkan eksekusi analisa yang sedang berjalan"),
    ("Ctrl + Q", "Keluar dari aplikasi AXIOM"),
    ("Enter", "Kirim pertanyaan riset / Buka run lama di sidebar"),
    ("Panah Atas / Bawah", "Navigasi riwayat input pertanyaan sebelumnya"),
    ("Ctrl + Y", "Salin teks markdown laporan ke clipboard"),
    ("Ctrl + S", "Simpan laporan aktif ke berkas .md lokal"),
    ("Tab / Shift + Tab", "Pindah fokus antar widget/panel"),
    ("Escape", "Tutup modal / dialog yang sedang terbuka"),
]

class HelpModal(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #help-dialog {
        width: 80;
        max-width: 90%;
        height: auto;
        max-height: 85%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    #help-dialog Label.title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #shortcuts-table {
        height: 10;
        margin-bottom: 1;
    }
    #help-btn-bar {
        align-horizontal: right;
    }
    """

    def compose(self):
        with Vertical(id="help-dialog"):
            yield Label("Panduan Bantuan & Pintasan Keyboard AXIOM", classes="title")
            yield Label("Daftar Pintasan Keyboard:")
            yield DataTable(id="shortcuts-table")

            yield Label("Contoh Pertanyaan Riset Quant:")
            t = Text()
            t.append("1. Bandingkan momentum 12-1 bulan vs buy-and-hold di saham LQ45 5 tahun terakhir.\n", style="bold cyan")
            t.append("2. Uji korelasi sektor perbankan vs BI rate selama siklus kenaikan suku bunga.\n", style="bold green")
            t.append("3. Hitung VaR (95% & 99%) portofolio 5 saham big cap Indonesia dengan historical simulation.\n", style="bold magenta")
            yield Static(t)

            with Horizontal(id="help-btn-bar"):
                yield Button("Tutup (Esc)", id="btn-close-help", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#shortcuts-table", DataTable)
        table.add_column("Tombol", width=22)
        table.add_column("Fungsi / Aksi", width=50)
        for key, desc in SHORTCUTS:
            table.add_row(key, desc)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
