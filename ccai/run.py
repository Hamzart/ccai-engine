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
from ccai.core.subsystems.analogical import AnalogicalReasoner
from ccai.core.subsystems.temporal import TemporalReasoner
from ccai.core.subsystems.hypothetical import HypotheticalReasoner
from ccai.external.fusion import KnowledgeFusion, ExternalKnowledgeSubsystem
from ccai.external.connector import registry
from ccai.external.wikipedia import wikipedia_connector
from ccai.external.websearch import websearch_connector
from ccai.llm.interface import LLMInterface

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
    
    # Initialize LLM interface
    llm_interface = LLMInterface()
    
    # Initialize knowledge fusion
    fusion = KnowledgeFusion(graph)
    
    subsystems = [
        InheritanceResolver(),
        RelationResolver(graph=graph),
        FuzzyMatch(),
        BayesianUpdater(),
        ConflictResolver(),
        AnalogicalReasoner(graph=graph),
        TemporalReasoner(),
        HypotheticalReasoner(graph=graph),
        ExternalKnowledgeSubsystem(graph=graph, fusion=fusion),
    ]
    reasoning_core = ReasoningCore(graph, subsystems)
    
    # --- 2. Load Knowledge ---
    print("🧠 Loading Concept Graph from disk...")
    graph.load_from_disk()

    # Always load the knowledge bases
    kb_file = Path("knowledge.txt")
    if kb_file.exists():
        print("📥 Loading knowledge base from knowledge.txt ...")
        extractor.ingest_text(kb_file.read_text())
        graph.save_snapshot()
        
    # Load common knowledge
    common_kb_file = Path("common_knowledge.txt")
    if common_kb_file.exists():
        print("📥 Loading common knowledge base ...")
        extractor.ingest_text(common_kb_file.read_text())
        graph.save_snapshot()
    
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
                        # Use both the traditional extractor and the LLM interface
                        extractor.ingest_text(learning_text)
                        llm_interface.extract_knowledge(learning_text)
                        graph.save_snapshot()
                        print(Panel("✅ Knowledge acquired and saved.", style="green"))
                elif text_stripped.startswith("@ingest"):
                    file_path_str = text_stripped.removeprefix("@ingest").strip()
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        print(Panel(f"📚 Ingesting knowledge from file: {file_path}", title="[cyan]Ingestion Mode[/cyan]", border_style="cyan"))
                        file_content = file_path.read_text()
                        extractor.ingest_text(file_content)
                        llm_interface.extract_knowledge(file_content)
                        graph.save_snapshot()
                        print(Panel("✅ Knowledge from file acquired and saved.", style="green"))
                elif text_stripped.startswith("@search"):
                    search_term = text_stripped.removeprefix("@search").strip()
                    if search_term:
                        print(Panel(f"🔍 Searching for information about: \"{search_term}\"", title="[blue]Search Mode[/blue]", border_style="blue"))
                        try:
                            # Use the Wikipedia connector to get information
                            wiki_info = wikipedia_connector.get_details(search_term)
                            if wiki_info and "summary" in wiki_info:
                                # Display the summary
                                print(Panel(wiki_info["summary"], title=f"[bold blue]Wikipedia: {search_term}[/bold blue]", border_style="blue"))
                                
                                # Learn from the information
                                if "summary" in wiki_info and wiki_info["summary"]:
                                    extractor.ingest_text(wiki_info["summary"])
                                    llm_interface.extract_knowledge(wiki_info["summary"])
                                    graph.save_snapshot()
                                    print(Panel("✅ Knowledge from Wikipedia acquired and saved.", style="green"))
                            else:
                                print(Panel(f"❌ No information found for \"{search_term}\" on Wikipedia.", title="[red]Search Failed[/red]", border_style="red"))
                        except Exception as e:
                            print(Panel(f"❌ Error searching Wikipedia: {str(e)}", title="[red]Search Error[/red]", border_style="red"))
                continue
                
            # --- Handle "define" command using IRA language module ---
            if text_stripped.startswith("define "):
                entity = text_stripped.removeprefix("define ").strip()
                if entity:
                    # Create a definition query
                    query_data = {
                        "entity": entity,
                        "query_type": "definition",
                        "attributes": {}
                    }
                    
                    # Generate response using the LLM interface
                    response = llm_interface.generate_response(query_data)
                    
                    # Display the response
                    print(Panel(response, title=f"[bold green]Definition[/bold green]", border_style="green"))
                    continue

            # --- Try IRA Language Module First ---
            # Parse the query using the LLM interface
            parsed_query = llm_interface.parse_query(text)
            
            # If the query was successfully parsed by the LLM interface
            if parsed_query and parsed_query.get("query_type") != "unknown":
                # Generate a response using the LLM interface
                response = llm_interface.generate_response(parsed_query)
                
                # Determine the appropriate panel title and style based on query type
                if parsed_query.get("query_type") == "greeting":
                    title = "Greeting"
                    style = "green"
                elif parsed_query.get("query_type") == "verification":
                    title = "Confirmation"
                    style = "green" if "Yes" in response else "red"
                elif parsed_query.get("query_type") == "definition":
                    title = "Definition"
                    style = "green"
                else:
                    title = parsed_query.get("query_type", "Response").capitalize()
                    style = "green"
                
                # Display the response
                print(Panel(response, title=f"[bold {style}]{title}[/bold {style}]", border_style=style))
                continue
            
            # --- Fallback to Traditional Processing ---
            # Normal Question Parsing
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
