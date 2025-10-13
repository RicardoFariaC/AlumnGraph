#!/usr/bin/env python3

import logging
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from typing_extensions import Annotated

from alumn.src.config import config
from alumn.src.graph import drawing, graph_handler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = typer.Typer()


def header() -> None:
    console = Console()
    console.print(
        Panel.fit(
            """
 █████╗ ██╗     ██╗   ██╗███╗   ███╗███╗   ██╗
██╔══██╗██║     ██║   ██║████╗ ████║████╗  ██║
███████║██║     ██║   ██║██╔████╔██║██╔██╗ ██║
██╔══██║██║     ██║   ██║██║╚██╔╝██║██║╚██╗██║
██║  ██║███████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝

System-Theoretic Process Analysis Graph Tool
    """,
            title="",
            border_style="dark_orange3",
        )
    )


@app.command()
def about() -> None:
    """
    Show information about the package.
    """
    header()
    typer.echo("AlumnGraph")
    typer.echo("Version: 0.1.0")
    typer.echo("Author: Ricardo Faria da Costa")
    typer.echo(
        "Description: A command-line tool for drawing STPA hierarchical models from JSON files.\n\n"
    )


@app.command()
def howto() -> None:
    """
    A How-To guide for defining JSON params to create graph.
    """
    header()
    typer.echo("""
    JSON Format Guide:
<<<<<<< HEAD

    1. Controllers: Define system components with id, label, and level
    2. Groups: Optional grouping of controllers with id, label and controllers_list
    3. Actions: Define control actions between components with from, to, action, feedback
    Example:
    {
        "controllers": [
            {"id": "cc", "label": "Central Command", "level": 0},
            {"id": "ofr", "label": "Officer", "level": 1},
        ],
        "groups": [
            {"id": "off_grp", "label": "Police office group", "controllers_list": ["cc","ofr"]}
        ],
        "actions": [
            {"from": "cc", "to": "ofr", "action": "Authorize", "feedback": "Status"}
        ]
    }
    """)


@app.command()
def paint(
    json_file: Annotated[str, typer.Argument(help="Path to the JSON file")],
    output_format: Annotated[
        Optional[str],
        typer.Option("--format", "-f", help="Output format (svg, png, pdf)"),
    ] = "svg",
    output_local: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Output local (/tmp/name.ext)"),
    ] = ".",
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging")
    ] = False,
) -> None:
    """
    Generate a dot graph from a JSON file.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    header()
    typer.echo("Generating graph from JSON file...\n\n")

    try:
        if output_format not in config.file.SUPPORTED_OUTPUT_FORMATS:
            typer.echo(
                f"Warning: Unsupported output format '{output_format}'. Using 'svg'."
            )
            output_format = "svg"

        graph = graph_handler.GraphHandler(json_file=json_file)
        action_list = drawing.set_action_list(graph)

        if output_local:
            drawing.define_diagram(graph, action_list, output_local)
        else:
            drawing.define_diagram(graph, action_list)

        typer.echo("✅ Graph generated successfully")
        typer.echo(f"📂 Output file: {output_local}.{output_format}")
    except FileNotFoundError as e:
        typer.echo(f"❌ Error: {e}")
    except Exception as e:
        typer.echo(f"❌ Unexpected Error: {e}")
        if verbose:
            logging.exception("Detailed error information: ")
        raise typer.Exit(1)


def run() -> None:
    app()


if __name__ == "__main__":
    app()
