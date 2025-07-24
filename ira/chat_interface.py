#!/usr/bin/env python3
"""
Chat interface for the IRA (Ideom Resolver AI) system.

This script provides a simple command-line interface for chatting with the IRA system,
using the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.
"""

import os
import sys
import cmd
import readline
import colorama
from pathlib import Path
from typing import Dict, Any
import nltk

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt tokenizer...")
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading punkt_tab tokenizer...")
    # The punkt_tab resource is part of the 'all' package
    nltk.download('all')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading stopwords...")
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading wordnet...")
    nltk.download('wordnet')

# Explicitly ensure punkt is downloaded and available
if not nltk.download('punkt', quiet=True):
    print("Warning: Failed to download punkt tokenizer. Some functionality may not work.")

from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.reasoning.temporal_context import TemporalContext
from ira.core.reasoning.signal_propagator import SignalPropagator
from ira.core.reasoning.text_processor import TextProcessor
from ira.core.reasoning.dynamic_response_generator import DynamicResponseGenerator
from ira.core.reasoning.learning_engine import LearningEngine, Feedback
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes
from ira.core.ira_system import IRASystem


# Initialize colorama for colored output
colorama.init()


def create_test_knowledge_graph():
    """
    Create a test Knowledge Graph with some concepts.
    
    Returns:
        A KnowledgeGraph instance with test concepts.
    """
    knowledge_graph = KnowledgeGraph()
    
    # Add some test concepts
    dog_concept = knowledge_graph.add_concept("dog")
    knowledge_graph.update_concept(
        dog_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "bark",
            "definition": "A domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking, howling, or whining voice."
        }
    )
    
    cat_concept = knowledge_graph.add_concept("cat")
    knowledge_graph.update_concept(
        cat_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "meow",
            "definition": "A small domesticated carnivorous mammal with soft fur, a short snout, and retractile claws."
        }
    )
    
    # Add a more complex concept with relationships
    animal_concept = knowledge_graph.add_concept("animal")
    knowledge_graph.update_concept(
        animal_concept.id,
        properties={
            "type": "category",
            "definition": "A living organism that feeds on organic matter, typically having specialized sense organs and nervous system and able to respond rapidly to stimuli."
        }
    )
    
    # Create relationships
    knowledge_graph.update_relation(dog_concept, animal_concept, "is_a", bidirectional=False)
    knowledge_graph.update_relation(cat_concept, animal_concept, "is_a", bidirectional=False)
    
    # Add some more concepts
    bird_concept = knowledge_graph.add_concept("bird")
    knowledge_graph.update_concept(
        bird_concept.id,
        properties={
            "type": "animal",
            "legs": "two",
            "wings": "two",
            "sound": "chirp",
            "definition": "A warm-blooded egg-laying vertebrate animal distinguished by the possession of feathers, wings, a beak, and typically by being able to fly."
        }
    )
    
    knowledge_graph.update_relation(bird_concept, animal_concept, "is_a", bidirectional=False)
    
    # Add a lion concept
    lion_concept = knowledge_graph.add_concept("lion")
    knowledge_graph.update_concept(
        lion_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "roar",
            "habitat": "savanna",
            "diet": "carnivore",
            "definition": "A large, carnivorous feline native to Africa, known for its mane in males and its role as an apex predator."
        }
    )
    knowledge_graph.update_relation(lion_concept, animal_concept, "is_a", bidirectional=False)
    
    # Add a multi-word concept
    golden_retriever_concept = knowledge_graph.add_concept("golden retriever")
    knowledge_graph.update_concept(
        golden_retriever_concept.id,
        properties={
            "type": "dog breed",
            "coat": "golden",
            "temperament": "friendly",
            "definition": "A medium-large gun dog that was bred to retrieve shot waterfowl, such as ducks and upland game birds, during hunting and shooting parties."
        }
    )
    
    knowledge_graph.update_relation(golden_retriever_concept, dog_concept, "is_a", bidirectional=False)
    
    # Add some computer-related concepts
    computer_concept = knowledge_graph.add_concept("computer")
    knowledge_graph.update_concept(
        computer_concept.id,
        properties={
            "type": "device",
            "definition": "An electronic device for storing and processing data, typically in binary form, according to instructions given to it in a variable program."
        }
    )
    
    programming_concept = knowledge_graph.add_concept("programming")
    knowledge_graph.update_concept(
        programming_concept.id,
        properties={
            "type": "activity",
            "definition": "The process of designing and building an executable computer program to accomplish a specific computing result or to perform a specific task."
        }
    )
    
    python_concept = knowledge_graph.add_concept("Python")
    knowledge_graph.update_concept(
        python_concept.id,
        properties={
            "type": "programming language",
            "creator": "Guido van Rossum",
            "year": "1991",
            "definition": "A high-level, interpreted programming language known for its readability and simplicity."
        }
    )
    
    knowledge_graph.update_relation(python_concept, programming_concept, "is_a_type_of", bidirectional=False)
    
    return knowledge_graph


def create_enhanced_ira_system():
    """
    Create an enhanced IRA system with the integration between the Unified Reasoning Core
    and the Knowledge Graph.
    
    Returns:
        An IRASystem instance with the enhanced integration.
    """
    # Create a Knowledge Graph
    knowledge_graph = create_test_knowledge_graph()
    
    # Create an Ideom Network
    ideom_network = IdeomNetwork()
    
    # Create a Temporal Context
    temporal_context = TemporalContext(max_history_size=10)
    
    # Create a Signal Propagator with temporal context
    signal_propagator = SignalPropagator(
        ideom_network=ideom_network,
        temporal_context=temporal_context
    )
    
    # Create a Unified Reasoning Core with enhanced components
    reasoning_core = UnifiedReasoningCore(
        ideom_network=ideom_network,
        signal_propagator=signal_propagator
    )
    
    # Create a Text Processor
    text_processor = TextProcessor(ideom_network=ideom_network)
    
    # Create a Dynamic Response Generator
    response_generator = DynamicResponseGenerator(ideom_network=ideom_network)
    
    # Create a Learning Engine
    learning_engine = LearningEngine(
        ideom_network=ideom_network,
        prefab_manager=reasoning_core.prefab_manager
    )
    
    # Create a Reasoning Knowledge Integration
    integration = ReasoningKnowledgeIntegration(
        knowledge_graph,
        reasoning_core
    )
    
    # Apply bug fixes
    apply_bug_fixes(integration)
    
    # Create an IRA System
    ira_system = IRASystem(
        knowledge_graph=knowledge_graph,
        ideom_network=ideom_network,
        reasoning_core=reasoning_core,
        reasoning_integration=integration
    )
    
    # Initialize the integration
    integration.create_ideoms_from_concepts()
    integration.create_prefabs_from_concepts()
    
    return ira_system


class IRAChatInterface(cmd.Cmd):
    """
    Command-line interface for chatting with the IRA system.
    """
    
    intro = colorama.Fore.CYAN + """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                  Welcome to the IRA Chat Interface           ║
    ║                                                              ║
    ║  IRA (Ideom Resolver AI) is an intelligent system based on   ║
    ║  the integration of a Unified Reasoning Core and a Knowledge ║
    ║  Graph. You can chat with IRA by typing your message and     ║
    ║  pressing Enter.                                             ║
    ║                                                              ║
    ║  Type 'help' for a list of commands.                         ║
    ║  Type 'exit' or 'quit' to exit.                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """ + colorama.Style.RESET_ALL
    
    prompt = colorama.Fore.GREEN + "You: " + colorama.Style.RESET_ALL
    
    def __init__(self):
        """Initialize the chat interface."""
        super().__init__()
        print("Initializing IRA system...")
        self.ira_system = create_enhanced_ira_system()
        print("IRA system initialized.")
        
        # Initialize conversation history
        self.conversation_history = []
    
    def default(self, line):
        """Process user input."""
        if line.lower() in ["exit", "quit"]:
            return self.do_exit(line)
        
        # Handle common conversational phrases
        conversational_responses = {
            "hi": "Hello! How can I help you today?",
            "hello": "Hello! How can I help you today?",
            "hey": "Hey there! What would you like to know?",
            "how are you": "I'm functioning well, thank you! How can I assist you?",
            "who are you": "I am IRA (Ideom Resolver AI), an intelligent system based on a unified reasoning core and knowledge graph. I can learn and answer questions about various topics.",
            "what can you do": "I can answer questions about topics I know, learn new information from you, and even learn from files or Wikipedia articles. Try asking me about animals, computers, or use commands like 'help' to see more options.",
            "can you talk": "Yes, I can communicate through text. I can answer questions, learn new information, and have simple conversations. What would you like to talk about?",
            "what are you": "I am IRA (Ideom Resolver AI), an intelligent system that uses a knowledge graph and reasoning core to understand and respond to your questions.",
            "thanks": "You're welcome! Is there anything else you'd like to know?",
            "thank you": "You're welcome! Is there anything else you'd like to know?"
        }
        
        # Check for conversational phrases
        for phrase, response in conversational_responses.items():
            if line.lower().strip() == phrase or line.lower().strip() == phrase + "?":
                print(colorama.Fore.BLUE + "IRA: " + colorama.Style.RESET_ALL + response)
                self.conversation_history.append({"user": line, "ira": response})
                return False
        
        # Check if the input is a statement of the form "X is Y"
        if " is " in line and not line.startswith("what") and not line.startswith("who") and not line.startswith("how") and not line.startswith("why") and not line.startswith("when") and not line.startswith("where"):
            parts = line.split(" is ", 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                object_or_property = parts[1].strip().rstrip(".")
                
                # Check if this is a property assignment or a relation
                if " a " in object_or_property or " an " in object_or_property:
                    # This is a relation (e.g., "X is a Y")
                    object_parts = object_or_property.split(" a ", 1)
                    if len(object_parts) != 2:
                        object_parts = object_or_property.split(" an ", 1)
                    
                    if len(object_parts) == 2:
                        object_value = object_parts[1].strip()
                        
                        # Add the relation to the knowledge graph
                        concept = self.ira_system.knowledge_graph.get_concept_by_name(subject)
                        if not concept:
                            concept = self.ira_system.knowledge_graph.add_concept(subject)
                        
                        object_concept = self.ira_system.knowledge_graph.get_concept_by_name(object_value)
                        if not object_concept:
                            object_concept = self.ira_system.knowledge_graph.add_concept(object_value)
                        
                        self.ira_system.knowledge_graph.update_relation(concept, object_concept, "is_a", bidirectional=False)
                        
                        response = f"I've learned that {subject} is a {object_value}."
                        
                        # Add to conversation history
                        self.conversation_history.append({"user": line, "ira": response})
                        
                        # Print the response
                        print(colorama.Fore.BLUE + "IRA: " + colorama.Style.RESET_ALL + response)
                        
                        return False
                else:
                    # This is a property assignment (e.g., "X is red")
                    property_value = object_or_property
                    
                    # Add the property to the knowledge graph
                    concept = self.ira_system.knowledge_graph.get_concept_by_name(subject)
                    if not concept:
                        concept = self.ira_system.knowledge_graph.add_concept(subject)
                    
                    self.ira_system.knowledge_graph.update_concept(
                        concept.id,
                        properties={
                            "definition": [property_value]
                        }
                    )
                    
                    response = f"I've learned that {subject} is {property_value}."
                    
                    # Add to conversation history
                    self.conversation_history.append({"user": line, "ira": response})
                    
                    # Print the response
                    print(colorama.Fore.BLUE + "IRA: " + colorama.Style.RESET_ALL + response)
                    
                    return False
        
        # Process the user input
        response = self.ira_system.process_message(line)
        
        # Add to conversation history
        self.conversation_history.append({"user": line, "ira": response})
        
        # Print the response
        print(colorama.Fore.BLUE + "IRA: " + colorama.Style.RESET_ALL + response)
        
        return False
    
    def do_exit(self, arg):
        """Exit the chat interface."""
        print(colorama.Fore.YELLOW + "Goodbye!" + colorama.Style.RESET_ALL)
        return True
    
    def do_help(self, arg):
        """Show help message."""
        print(colorama.Fore.CYAN + """
        Commands:
        - help: Show this help message.
        - exit, quit: Exit the chat interface.
        - clear: Clear the screen.
        - history: Show conversation history.
        - save [filename]: Save conversation history to a file.
        - learn_file <file_path>: Learn knowledge from a file.
        - learn_wiki <title>: Learn knowledge from a Wikipedia article.
        - search_wiki <query>: Search Wikipedia for articles.
        
        You can chat with IRA by typing your message and pressing Enter.
        Try asking questions about animals, computers, or programming.
        
        Example questions:
        - What is a dog?
        - What sound does a cat make?
        - What is a golden retriever?
        - What is Python?
        - Tell me about programming.
        
        You can also make statements to teach IRA new things:
        - Dogs are loyal companions.
        - Python is a popular programming language.
        """ + colorama.Style.RESET_ALL)
    
    def do_clear(self, arg):
        """Clear the screen."""
        os.system("cls" if os.name == "nt" else "clear")
        print(self.intro)
    
    def do_history(self, arg):
        """Show conversation history."""
        if not self.conversation_history:
            print(colorama.Fore.YELLOW + "No conversation history yet." + colorama.Style.RESET_ALL)
            return
        
        print(colorama.Fore.CYAN + "Conversation History:" + colorama.Style.RESET_ALL)
        for i, exchange in enumerate(self.conversation_history, 1):
            print(colorama.Fore.CYAN + f"--- Exchange {i} ---" + colorama.Style.RESET_ALL)
            print(colorama.Fore.GREEN + "You: " + colorama.Style.RESET_ALL + exchange["user"])
            print(colorama.Fore.BLUE + "IRA: " + colorama.Style.RESET_ALL + exchange["ira"])
    
    def do_save(self, arg):
        """Save conversation history to a file."""
        if not self.conversation_history:
            print(colorama.Fore.YELLOW + "No conversation history to save." + colorama.Style.RESET_ALL)
            return
        
        filename = arg.strip() or "ira_conversation.txt"
        with open(filename, "w") as f:
            f.write("IRA Conversation History\n")
            f.write("=======================\n\n")
            for i, exchange in enumerate(self.conversation_history, 1):
                f.write(f"--- Exchange {i} ---\n")
                f.write(f"You: {exchange['user']}\n")
                f.write(f"IRA: {exchange['ira']}\n\n")
        
        print(colorama.Fore.YELLOW + f"Conversation history saved to {filename}" + colorama.Style.RESET_ALL)
    
    def do_learn_file(self, arg):
        """Learn knowledge from a file."""
        if not arg:
            print(colorama.Fore.YELLOW + "Please specify a file path." + colorama.Style.RESET_ALL)
            return
        
        try:
            result = self.ira_system.learn_from_file(arg)
            
            if result["success"]:
                print(colorama.Fore.GREEN + "Successfully learned from file:" + colorama.Style.RESET_ALL)
                print(f"- Chunks processed: {result.get('chunks_processed', 0)}")
                print(f"- Concepts created: {len(result.get('concepts_created', []))}")
                print(f"- Relations created: {len(result.get('relations_created', []))}")
                
                # Add to conversation history
                self.conversation_history.append({
                    "user": f"learn_file {arg}",
                    "ira": f"Successfully learned from file {arg}. Created {len(result.get('concepts_created', []))} concepts and {len(result.get('relations_created', []))} relations."
                })
            else:
                print(colorama.Fore.RED + f"Failed to learn from file: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + f"Error learning from file: {str(e)}" + colorama.Style.RESET_ALL)
    
    def do_learn_wiki(self, arg):
        """Learn knowledge from a Wikipedia article."""
        if not arg:
            print(colorama.Fore.YELLOW + "Please specify a Wikipedia article title." + colorama.Style.RESET_ALL)
            return
        
        try:
            print(colorama.Fore.YELLOW + f"Fetching Wikipedia article: {arg}..." + colorama.Style.RESET_ALL)
            result = self.ira_system.learn_from_wikipedia(arg)
            
            if result["success"]:
                print(colorama.Fore.GREEN + f"Successfully learned from Wikipedia article: {result.get('title', arg)}" + colorama.Style.RESET_ALL)
                print(f"- Chunks processed: {result.get('chunks_processed', 0)}")
                print(f"- Concepts created: {len(result.get('concepts_created', []))}")
                print(f"- Relations created: {len(result.get('relations_created', []))}")
                
                # Add to conversation history
                self.conversation_history.append({
                    "user": f"learn_wiki {arg}",
                    "ira": f"Successfully learned from Wikipedia article '{result.get('title', arg)}'. Created {len(result.get('concepts_created', []))} concepts and {len(result.get('relations_created', []))} relations."
                })
            else:
                print(colorama.Fore.RED + f"Failed to learn from Wikipedia article: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + f"Error learning from Wikipedia article: {str(e)}" + colorama.Style.RESET_ALL)
    
    def do_search_wiki(self, arg):
        """Search Wikipedia for articles."""
        if not arg:
            print(colorama.Fore.YELLOW + "Please specify a search query." + colorama.Style.RESET_ALL)
            return
        
        try:
            print(colorama.Fore.YELLOW + f"Searching Wikipedia for: {arg}..." + colorama.Style.RESET_ALL)
            result = self.ira_system.search_wikipedia(arg)
            
            if result["success"]:
                print(colorama.Fore.GREEN + f"Search results for: {result.get('query', arg)}" + colorama.Style.RESET_ALL)
                for i, article in enumerate(result.get("results", []), 1):
                    print(f"{i}. {article.get('title', 'Unknown')}")
                    print(f"   {article.get('snippet', 'No snippet available')}")
                    print()
                
                print(colorama.Fore.YELLOW + "To learn from an article, use 'learn_wiki <title>'." + colorama.Style.RESET_ALL)
                
                # Add to conversation history
                self.conversation_history.append({
                    "user": f"search_wiki {arg}",
                    "ira": f"Found {len(result.get('results', []))} Wikipedia articles for '{result.get('query', arg)}'."
                })
            else:
                print(colorama.Fore.RED + f"Failed to search Wikipedia: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + f"Error searching Wikipedia: {str(e)}" + colorama.Style.RESET_ALL)
    
    def do_learn_wiki_search(self, arg):
        """Learn from Wikipedia articles matching a search query."""
        if not arg:
            print(colorama.Fore.YELLOW + "Please specify a search query." + colorama.Style.RESET_ALL)
            return
        
        try:
            print(colorama.Fore.YELLOW + f"Searching and learning from Wikipedia articles about: {arg}..." + colorama.Style.RESET_ALL)
            result = self.ira_system.learn_from_wikipedia_search(arg)
            
            if result["success"]:
                print(colorama.Fore.GREEN + f"Successfully learned from Wikipedia articles about: {result.get('query', arg)}" + colorama.Style.RESET_ALL)
                print(f"- Articles processed: {result.get('articles_processed', 0)} of {result.get('total_articles', 0)}")
                print(f"- Concepts created: {len(result.get('concepts_created', []))}")
                print(f"- Relations created: {len(result.get('relations_created', []))}")
                
                # Add to conversation history
                self.conversation_history.append({
                    "user": f"learn_wiki_search {arg}",
                    "ira": f"Successfully learned from {result.get('articles_processed', 0)} Wikipedia articles about '{result.get('query', arg)}'. Created {len(result.get('concepts_created', []))} concepts and {len(result.get('relations_created', []))} relations."
                })
            else:
                print(colorama.Fore.RED + f"Failed to learn from Wikipedia search: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + f"Error learning from Wikipedia search: {str(e)}" + colorama.Style.RESET_ALL)


def main():
    """Run the IRA chat interface."""
    chat_interface = IRAChatInterface()
    try:
        chat_interface.cmdloop()
    except KeyboardInterrupt:
        print(colorama.Fore.YELLOW + "\nGoodbye!" + colorama.Style.RESET_ALL)


if __name__ == "__main__":
    main()