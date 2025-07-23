# ccai/cli/main.py

from pathlib import Path
import typer
from rich import print, print_json

from ccai.core.graph import ConceptGraph
from ccai.core.models import ConceptNode
from ccai.nlp.extractor import InformationExtractor

# This CLI is now purely for development and data management.
app = typer.Typer(help="A CLI tool to manage the CC-AI's knowledge graph.")

# Initialize components needed for the CLI
STORAGE_DIR = Path("graph_data")
graph = ConceptGraph(STORAGE_DIR)
extractor = InformationExtractor(graph)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Loads the graph and displays help if no command is given."""
    graph.load_from_disk()
    if ctx.invoked_subcommand is None:
        print("✅ Graph loaded. Use a subcommand like 'ingest' or 'show'.")


@app.command()
def ingest(file_path: Path):
    """Ingests knowledge from a plain text file."""
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        raise typer.Exit(1)
    
    print(f"📚 Ingesting text from {file_path}...")
    text_content = file_path.read_text()
    extractor.ingest_text(text_content)
    graph.save_snapshot()
    print("✅ Ingestion complete and snapshot saved.")

@app.command()
def show(name: str):
    """Displays the data for a specific node in JSON format."""
    node = graph.get_node(name)
    if node:
        print_json(node.model_dump_json(indent=2))
    else:
        print(f"Error: Node '{name}' not found.")

if __name__ == "__main__":
    app()
