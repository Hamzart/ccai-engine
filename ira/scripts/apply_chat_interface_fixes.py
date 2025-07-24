#!/usr/bin/env python3
"""
Script to apply all the fixes to the IRA chat interface.

This script applies all the fixes described in the CHAT_INTERFACE_FIXES.md document.
It modifies the following files:
- ira/chat_interface.py
- ira/core/ira_system.py
- ira/core/reasoning/unified_reasoning_core.py
"""

import os
import sys
import re
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def apply_fixes():
    """Apply all the fixes to the IRA chat interface."""
    print("Applying fixes to the IRA chat interface...")
    
    # Fix 1: Add "lion" concept to test knowledge graph
    fix_chat_interface()
    
    # Fix 2: Improve response generation for unknown concepts
    fix_ira_system()
    
    # Fix 3: Enhance fallback response mechanism
    fix_unified_reasoning_core()
    
    print("All fixes applied successfully!")

def fix_chat_interface():
    """Add "lion" concept to test knowledge graph in chat_interface.py."""
    file_path = project_root / "ira" / "chat_interface.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check if the fix has already been applied
    if "lion_concept = knowledge_graph.add_concept(\"lion\")" in content:
        print("Fix 1: Already applied to chat_interface.py")
        return
    
    # Find the position to insert the lion concept
    pattern = r"knowledge_graph\.update_relation\(bird_concept, animal_concept, \"is_a\", bidirectional=False\)\s+"
    pattern += r"# Add a multi-word concept"
    
    replacement = """knowledge_graph.update_relation(bird_concept, animal_concept, "is_a", bidirectional=False)
    
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
    
    # Add a multi-word concept"""
    
    modified_content = re.sub(pattern, replacement, content)
    
    # Add special handler for conversational phrases
    pattern = r"def default\(self, line\):\s+"
    pattern += r"\"\"\"Process user input\.\"\"\"\s+"
    pattern += r"if line\.lower\(\) in \[\"exit\", \"quit\"\]:\s+"
    pattern += r"return self\.do_exit\(line\)\s+"
    pattern += r"\s+"
    pattern += r"# Check if the input is a statement of the form \"X is Y\""
    
    replacement = """def default(self, line):
        # Process user input.
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
        
        # Check if the input is a statement of the form "X is Y\""""
    
    modified_content = re.sub(pattern, replacement, modified_content)
    
    with open(file_path, "w") as f:
        f.write(modified_content)
    
    print("Fix 1: Applied to chat_interface.py")

def fix_ira_system():
    """Improve response generation for unknown concepts in ira_system.py."""
    file_path = project_root / "ira" / "core" / "ira_system.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check if the fix has already been applied
    if "if not result[\"properties\"] and not result[\"relations\"]:" in content:
        print("Fix 2: Already applied to ira_system.py")
        return
    
    # Fix the _generate_response_from_query_result method
    pattern = r"elif result\[\"type\"\] == \"general\":\s+"
    pattern += r"# Generate a response based on the properties and relations\s+"
    pattern += r"response = f\"Here's what I know about {result\['concept'\]}:\\n\"\s+"
    pattern += r"\s+"
    pattern += r"# Add properties\s+"
    pattern += r"if result\[\"properties\"\]:\s+"
    pattern += r"response \+= \"Properties:\\n\"\s+"
    pattern += r"for name, value in result\[\"properties\"\]\.items\(\):\s+"
    pattern += r"response \+= f\"- {name}: {value}\\n\"\s+"
    pattern += r"\s+"
    pattern += r"# Add relations\s+"
    pattern += r"if result\[\"relations\"\]:\s+"
    pattern += r"response \+= \"Relations:\\n\"\s+"
    pattern += r"for relation in result\[\"relations\"\]:\s+"
    pattern += r"response \+= f\"- {relation\['type'\]} {relation\['target'\]}\\n\"\s+"
    pattern += r"\s+"
    pattern += r"return response"
    
    replacement = """elif result["type"] == "general":
            # Generate a response based on the properties and relations
            response = f"Here's what I know about {result['concept']}:\\n"
            
            # Add properties
            if result["properties"]:
                response += "Properties:\\n"
                for name, value in result["properties"].items():
                    response += f"- {name}: {value}\\n"
            
            # Add relations
            if result["relations"]:
                response += "Relations:\\n"
                for relation in result["relations"]:
                    response += f"- {relation['type']} {relation['target']}\\n"
            
            # If there are no properties or relations, provide a helpful message
            if not result["properties"] and not result["relations"]:
                response = f"I don't have any information about {result['concept']} yet. You can teach me about it by making statements like '{result['concept']} is a [type]' or '{result['concept']} has [property]'."
            
            return response"""
    
    modified_content = re.sub(pattern, replacement, content)
    
    # Add the _sync_ideoms_with_knowledge_graph method
    pattern = r"def process_message\(self, message: str, context_id: Optional\[str\] = None\) -> str:\s+"
    pattern += r"\"\"\".*?\"\"\".*?"
    pattern += r"# Process the message using the Unified Reasoning Core\s+"
    pattern += r"reasoning_result = self\.reasoning_core\.process\(message\)\s+"
    pattern += r"\s+"
    pattern += r"# Process the message using the Reasoning Knowledge Integration"
    
    replacement = """def process_message(self, message: str, context_id: Optional[str] = None) -> str:
        # Process a user message and generate a response.
        #
        # Args:
        #     message: The user message.
        #     context_id: The ID of the conversation context to use.
        #         If None, the active context will be used, or a new one will be created.
        #
        # Returns:
        #     The response to the user message.
        # Extract knowledge from the message
        context = self.conversation_manager._get_or_create_context(context_id)
        knowledge = self.conversation_integration.extract_knowledge(message, context)
        
        # Check if the message is a question about a concept
        if message.lower().startswith("what is") or message.lower().startswith("who is") or message.lower().startswith("tell me about"):
            # Extract the concept name from the message
            concept_name = message.lower().replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            concept_name = concept_name.rstrip("?").strip()
            
            # Check if the concept exists in the knowledge graph
            concept = self.knowledge_graph.get_concept_by_name(concept_name)
            if concept:
                # Get the concept's properties and relations
                properties_dict = {}
                for name, prop_value in concept.get_properties().items():
                    properties_dict[name] = prop_value.get_value()
                
                relations_list = []
                for relation in concept.get_all_relations():
                    target_concept = self.knowledge_graph.get_concept_by_id(relation.target_concept_id)
                    if target_concept:
                        relations_list.append({
                            "type": relation.type,
                            "target": target_concept.name,
                            "confidence": 1.0
                        })
                
                # Create a query result
                result = {
                    "type": "general",
                    "concept": concept_name,
                    "properties": properties_dict,
                    "relations": relations_list,
                    "success": True
                }
                
                # Generate a response based on the query result
                return self._generate_response_from_query_result(result)
        
        # Process the message using the Unified Reasoning Core
        reasoning_result = self.reasoning_core.process(message)
        
        # Ensure new ideoms are added to the knowledge graph
        self._sync_ideoms_with_knowledge_graph(reasoning_result.get_activation_pattern())
        
        # Process the message using the Reasoning Knowledge Integration"""
    
    modified_content = re.sub(pattern, replacement, modified_content)
    
    # Add the _sync_ideoms_with_knowledge_graph method
    pattern = r"def run_cli\(self\):"
    
    replacement = """def _sync_ideoms_with_knowledge_graph(self, activation_pattern):
        # Ensure that ideoms in the activation pattern are also represented as concepts in the knowledge graph.
        #
        # Args:
        #     activation_pattern: The activation pattern containing ideoms.
        # Get the active ideoms from the activation pattern
        active_ideom_ids = activation_pattern.get_active_ideoms()
        
        for ideom_id in active_ideom_ids:
            # Get the ideom from the ideom network
            ideom = self.reasoning_core.ideom_network.get_ideom(ideom_id)
            
            if ideom:
                # Check if a concept with the same name already exists in the knowledge graph
                concept = self.knowledge_graph.get_concept_by_name(ideom.name)
                
                if not concept:
                    # Create a new concept in the knowledge graph
                    self.knowledge_graph.add_concept(ideom.name)
    
    def run_cli(self):"""
    
    modified_content = re.sub(pattern, replacement, modified_content)
    
    with open(file_path, "w") as f:
        f.write(modified_content)
    
    print("Fix 2: Applied to ira_system.py")

def fix_unified_reasoning_core():
    """Enhance fallback response mechanism in unified_reasoning_core.py."""
    file_path = project_root / "ira" / "core" / "reasoning" / "unified_reasoning_core.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check if the fix has already been applied
    if "question_indicators = [\"what\", \"who\", \"how\", \"why\", \"when\", \"where\", \"is\", \"are\", \"can\", \"do\", \"does\"]" in content:
        print("Fix 3: Already applied to unified_reasoning_core.py")
        return
    
    # Fix the _generate_generic_response method
    pattern = r"def _generate_generic_response\(self, activation_pattern: ActivationPattern\) -> str:\s+"
    pattern += r"\"\"\".*?\"\"\".*?"
    pattern += r"# Get the most active ideoms\s+"
    pattern += r"most_active_ideoms = activation_pattern\.get_most_active_ideoms\(5\)\s+"
    pattern += r"ideom_names = \[\]\s+"
    pattern += r"\s+"
    pattern += r"for ideom_id in most_active_ideoms:\s+"
    pattern += r"ideom = self\.ideom_network\.get_ideom\(ideom_id\)\s+"
    pattern += r"if ideom:\s+"
    pattern += r"ideom_names\.append\(ideom\.name\)\s+"
    pattern += r"\s+"
    pattern += r"# Generate a response based on the most active ideoms\s+"
    pattern += r"if ideom_names:\s+"
    pattern += r"return f\"I'm thinking about: {', '\.join\(ideom_names\)}\"\s+"
    pattern += r"else:\s+"
    pattern += r"return \"I'm not sure how to respond to that\.\""
    
    replacement = """def _generate_generic_response(self, activation_pattern: ActivationPattern) -> str:
        # Generate a generic response based on the activation pattern.
        #
        # Args:
        #     activation_pattern: The activation pattern.
        #
        # Returns:
        #     A generic response.
        # Get the most active ideoms
        most_active_ideoms = activation_pattern.get_most_active_ideoms(5)
        ideom_names = []
        
        for ideom_id in most_active_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                ideom_names.append(ideom.name)
        
        # Generate a more helpful response based on the most active ideoms
        if ideom_names:
            # Check if it's likely a question
            question_indicators = ["what", "who", "how", "why", "when", "where", "is", "are", "can", "do", "does"]
            is_question = any(name.lower() in question_indicators for name in ideom_names)
            
            if is_question:
                return f"I don't have enough information to answer questions about {', '.join(ideom_names)}. You can teach me by making statements about these topics."
            else:
                return f"I understand you're talking about {', '.join(ideom_names)}, but I don't have enough knowledge to provide a detailed response. You can teach me more about these topics."
        else:
            return "I don't understand that yet. You can teach me by making simple statements or asking me about things I already know.\""""
    
    modified_content = re.sub(pattern, replacement, content)
    
    with open(file_path, "w") as f:
        f.write(modified_content)
    
    print("Fix 3: Applied to unified_reasoning_core.py")

if __name__ == "__main__":
    apply_fixes()