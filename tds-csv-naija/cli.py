"""tds-csv — quickly explore a CSV file."""

from pathlib import Path
from importlib.metadata import version as _v

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

__version__ = _v("tds-csv-naija")

app = typer.Typer(
    name="tds-csv",
    help="Quickly explore a CSV file.",
    add_completion=False,
)
console = Console()


def _render(df: pd.DataFrame, title: str) -> None:
    table = Table(title=title, show_lines=True)
    for col in df.columns:
        table.add_column(str(col), style="cyan")
    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row])
    console.print(table)


@app.command()
def main(
    file: Path = typer.Argument(
        ..., exists=True, readable=True, help="CSV file to read."
    ),
    top: int = typer.Option(10, help="Show top N rows."),
    by: str | None = typer.Option(None, help="Sort by column (default: first column)."),
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
) -> None:
    """Render a CSV file as a pretty table."""
    if version:
        console.print(f"tds-csv v{__version__}")
        raise typer.Exit()

    df = pd.read_csv(file)
    sort_col = by or df.columns[0]
    if sort_col not in df.columns:
        console.print(f"[red]Column '{sort_col}' not in CSV[/red]")
        raise typer.Exit(code=1)
    df = df.sort_values(by=sort_col, ascending=False).head(top)
    _render(df, f"{file.name} — top {top} by {sort_col}")


if __name__ == "__main__":
    app()
