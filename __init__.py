from src.graph import drawing, graph_handler
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.panel import Panel

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

app = typer.Typer()

@app.command()
def about():
    """
    Show information about the package.
    """
    typer.echo("AlumnGraph")
    typer.echo("Version: 0.1.0")
    typer.echo("Author: Ricardo Faria da Costa")
    typer.echo("Description: A command-line tool for drawing STPA hierarchical models from JSON files.\n\n")

@app.command()
def howto():
    """
    A How-To guide for defining JSON params to create graph.
    """


@app.command()
def generate(
        json_file: Annotated[str, typer.Argument(help="Path to the JSON file")],
    ):
    """
    Generate a dot graph from a JSON file.
    """
    typer.echo("Generating graph from JSON file...\n\n")

    graph = graph_handler.GraphHandler(json_file=json_file)
    action_list = drawing.set_action_list(graph)
    
    drawing.define_diagram(drawing.GraphHandler(json_file=json_file), action_list)

if __name__ == "__main__":
    app()