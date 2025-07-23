# run.py

import shutil
import sys
from pathlib import Path
from rich import print
from rich.panel import Panel

from ccai.core.graph import ConceptGraph
from ccai.nlp.parser import QueryParser
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.primitives import PrimitiveManager
from ccai.core.reasoning import ReasoningCore
from ccai.core.subsystems.inheritance import InheritanceResolver
from ccai.core.subsystems.relation import RelationResolver
from ccai.core.subsystems.fuzzy import FuzzyMatch
from ccai.core.subsystems.bayes import BayesianUpdater
from ccai.core.subsystems.conflict import ConflictResolver

def run_chat_session():
    """Initializes all AI components and starts the interactive chat loop."""
    
    # --- 1. Initialize All Core Components ---
    print("🤖 Initializing AI...")
    storage_dir = Path("graph_data")
    primitives_file = Path("primitives.json")
    
    graph = ConceptGraph(storage_dir)
    primitive_manager = PrimitiveManager(primitives_file)
    query_parser = QueryParser()
    extractor = InformationExtractor(graph, primitive_manager)
    
    subsystems = [
        InheritanceResolver(),
        RelationResolver(graph=graph),
        FuzzyMatch(),
        BayesianUpdater(),
        ConflictResolver(),
    ]
    reasoning_core = ReasoningCore(graph, subsystems)
    
    # --- 2. Load Knowledge ---
    print("🧠 Loading Concept Graph from disk...")
    graph.load_from_disk()
    
    # --- 3. Start Chat Loop ---
    print("✅ AI Ready. Let's chat! (Hint: try '@forget_all' to reset memory)")
    print("-" * 50)

    while True:
        try:
            text = input("You> ")
            if text.lower() in ["exit", "quit"]:
                break

            text_stripped = text.strip()

            # --- Command Handling ---
            if text_stripped.startswith("@"):
                if text_stripped == "@forget_all":
                    print(Panel("🔥 Erasing all learned knowledge...", style="bold red"))
                    if storage_dir.exists():
                        shutil.rmtree(storage_dir)
                    print(Panel("✅ All knowledge has been erased.\nThe application will now exit. Please restart it to begin with a clean slate.", title="Reset Complete", border_style="green"))
                    sys.exit() # Exit the application

                if text_stripped.startswith("@learn"):
                    learning_text = text_stripped.removeprefix("@learn").strip()
                    if learning_text:
                        print(Panel(f"🧠 Learning: \"{learning_text}\"", title="[yellow]Learning Mode[/yellow]", border_style="yellow"))
                        extractor.ingest_text(learning_text)
                        graph.save_snapshot()
                        print(Panel("✅ Knowledge acquired and saved.", style="green"))
                elif text_stripped.startswith("@ingest"):
                    file_path_str = text_stripped.removeprefix("@ingest").strip()
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        print(Panel(f"📚 Ingesting knowledge from file: {file_path}", title="[cyan]Ingestion Mode[/cyan]", border_style="cyan"))
                        extractor.ingest_text(file_path.read_text())
                        graph.save_snapshot()
                        print(Panel("✅ Knowledge from file acquired and saved.", style="green"))
                continue

            # --- Normal Question Parsing ---
            initial_signal = query_parser.parse_question(text)

            if not initial_signal:
                print(Panel("[bold red]Sorry, I couldn't understand the structure of your question.[/bold red]", title="Parse Error", border_style="red"))
                continue

            if not graph.get_node(initial_signal.origin):
                print(Panel(f"I don't have any information about '{initial_signal.origin}'.", title="[yellow]Unknown Concept[/yellow]", border_style="yellow"))
                continue

            results = reasoning_core.process_signal(initial_signal)
            
            if initial_signal.purpose == 'VERIFY':
                is_confirmed = any(res.payload.get('confirmed') for res in results)
                if is_confirmed:
                    print(Panel("Yes.", title="[bold green]Confirmation[/bold green]", border_style="green"))
                else:
                    print(Panel("As far as I know, no.", title="[bold red]Confirmation[/bold red]", border_style="red"))
            else: # Handle QUERY
                final_answers = set()
                for res in results:
                    if 'final_answer' in res.payload:
                        final_answers.add(res.payload['final_answer'])
                    elif 'answer' in res.payload:
                        final_answers.add(res.payload['answer'])

                if final_answers:
                    print(Panel("\n".join(f"- {ans}" for ans in sorted(list(final_answers))), title="[bold green]Answer[/bold green]", border_style="green"))
                else:
                    print(Panel("[yellow]I couldn't find a definitive answer through reasoning.[/yellow]", title="Result", border_style="yellow"))

        except (KeyboardInterrupt, EOFError):
            break
            
    print("\n🤖 Goodbye!")

if __name__ == "__main__":
    run_chat_session()
