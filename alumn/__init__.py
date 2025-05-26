#!/usr/bin/env python3

from alumn.src.graph import drawing, graph_handler
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

app = typer.Typer()


def header():
    console = Console()
    console.print(Panel.fit("""
 █████╗ ██╗     ██╗   ██╗███╗   ███╗███╗   ██╗
██╔══██╗██║     ██║   ██║████╗ ████║████╗  ██║
███████║██║     ██║   ██║██╔████╔██║██╔██╗ ██║
██╔══██║██║     ██║   ██║██║╚██╔╝██║██║╚██╗██║
██║  ██║███████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝

System-Theoretic Process Analysis Graph Tool
    """, title="", border_style="dark_orange3"))

@app.command()
def about():
    """
    Show information about the package.
    """
    header()
    typer.echo("AlumnGraph")
    typer.echo("Version: 0.1.0")
    typer.echo("Author: Ricardo Faria da Costa")
    typer.echo("Description: A command-line tool for drawing STPA hierarchical models from JSON files.\n\n")

@app.command()
def howto():
    """
    A How-To guide for defining JSON params to create graph.
    """
    header()

@app.command()
def paint(
        json_file: Annotated[str, typer.Argument(help="Path to the JSON file")],
    ):
    """
    Generate a dot graph from a JSON file.
    """
    header()
    typer.echo("Generating graph from JSON file...\n\n")
    graph = graph_handler.GraphHandler(json_file=json_file)
    action_list = drawing.set_action_list(graph)
    drawing.define_diagram(graph, action_list) 

def run():
    app()

if __name__ == "__main__":
    app()