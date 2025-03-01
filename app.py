from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer
from textual.binding import Binding
import polars as pl
from textual import work
import asyncio

class LivePolarsApp(App):
    """A terminal-based live viewer for Polars DataFrames with Vim-inspired navigation."""

    CSS = """
    DataTable {
        background: $background;
        border: none;
        height: 100%;
        width: 100%;
    }

    DataTable.--cursor {
        border: none;  # Remove cursor border for a cleaner look
    }

    DataTable .table_cell {
        border: none;  # Remove cell borders for sleekness
        padding: 0 1;  # Minimal padding
    }

    Footer {
        background: $background-darken-1;
        color: $text-muted;
    }

    Screen {
        background: #1a1a1a;  # Dark background like Harlequin
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "cursor_left", "Move left (h)", show=False),
        Binding("j", "cursor_down", "Move down (j)", show=False),
        Binding("k", "cursor_up", "Move up (k)", show=False),
        Binding("l", "cursor_right", "Move right (l)", show=False),
        Binding("gg", "go_to_top", "Go to top (gg)", show=False),
        Binding("G", "go_to_bottom", "Go to bottom (G)", show=False),
    ]

    def __init__(self, df: pl.DataFrame):
        self.df = df
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the app with a DataTable and Footer."""
        yield DataTable(id="polars_table")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the DataTable with Polars data."""
        self.update_table()
        self.refresh_loop()  # Changed from start_refresh_loop to refresh_loop

    def update_table(self):
        """Update the DataTable with current Polars DataFrame data."""
        try:
            table = self.query_one(DataTable)
            table.clear()
            table.add_columns(*self.df.columns)
            for row in self.df.rows():
                table.add_row(*map(str, row))
        except Exception as e:
            self.notify(f"Error updating table: {e}", severity="error")

    @work
    async def refresh_loop(self):
        """Periodically refresh the table to reflect DataFrame changes."""
        while True:
            await asyncio.sleep(1)  # Poll every second—tweak as needed
            self.update_table()

    def action_cursor_left(self):
        """Move cursor left (Vim 'h')."""
        table = self.query_one(DataTable)
        table.cursor_left()

    def action_cursor_down(self):
        """Move cursor down (Vim 'j')."""
        table = self.query_one(DataTable)
        table.cursor_down()

    def action_cursor_up(self):
        """Move cursor up (Vim 'k')."""
        table = self.query_one(DataTable)
        table.cursor_up()

    def action_cursor_right(self):
        """Move cursor right (Vim 'l')."""
        table = self.query_one(DataTable)
        table.cursor_right()

    def action_go_to_top(self):
        """Move to the top of the table (Vim 'gg')."""
        table = self.query_one(DataTable)
        table.move_cursor(row=0, col=0)

    def action_go_to_bottom(self):
        """Move to the bottom of the table (Vim 'G')."""
        table = self.query_one(DataTable)
        table.move_cursor(row=len(table.rows) - 1, col=0)

if __name__ == "__main__":
    # Example Polars DataFrame
    df = pl.DataFrame(
        {"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "score": [88.5, 92.0, 77.5]}
    )
    app = LivePolarsApp(df)
    app.run()