"""Sidebar widget displaying data files in data/ directory."""
import os
from textual.widget import Widget
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option
from rich.text import Text

class SidebarData(Widget):
    DEFAULT_CSS = """
    SidebarData {
        height: 1fr;
    }
    SidebarData Label {
        background: $primary-darken-2;
        color: $text;
        text-style: bold;
        padding: 0 1;
        width: 100%;
    }
    SidebarData OptionList {
        height: 1fr;
        scrollbar-size-vertical: 1;
    }
    """

    def __init__(self, data_dir: str = "data", **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir

    def compose(self):
        yield Label("DATA (file di data/)")
        yield OptionList(id="data-option-list")

    def on_mount(self) -> None:
        self.refresh_files()

    def refresh_files(self) -> None:
        option_list = self.query_one("#data-option-list", OptionList)
        option_list.clear_options()

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

        files = sorted(os.listdir(self.data_dir))
        if not files:
            option_list.add_option(Option("[dim]Folder data/ kosong[/dim]", disabled=True))
            return

        for fname in files:
            fpath = os.path.join(self.data_dir, fname)
            if os.path.isfile(fpath):
                size_kb = os.path.getsize(fpath) / 1024
                ext = fname.split(".")[-1].upper() if "." in fname else "FILE"
                
                t = Text()
                t.append(f"[{ext}] ", style="bold cyan")
                t.append(fname, style="bold")
                t.append(f" ({size_kb:.1f} KB)", style="dim")
                option_list.add_option(Option(t, id=fname))
