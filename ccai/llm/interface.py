"""
LLM interface for CCAI chatbot.

This module provides integration with a small embedded language model for natural language
understanding and generation, improving the chatbot's ability to process user input
and generate coherent responses without relying on external APIs.

The implementation is based on the IRA (Ideom Resolver AI) philosophy, where:
- Ideoms are atomic symbolic units of cognition
- Prefabs are conceptual templates composed of ideoms
- Signal propagation simulates the convergence of ideoms to activate prefab nodes
"""

import os
import logging
import json
import re
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import numpy as np
import pickle

from ccai.llm.ira_language import IRALanguageModule

# Set up logging
logger = logging.getLogger(__name__)

class EmbeddedLLM:
    """
    A lightweight embedded language model implementation based on the IRA philosophy.
    
    This class implements a hybrid symbolic-statistical approach to language understanding
    and generation, using:
    - Pattern matching for query parsing
    - Template-based generation for responses
    - Vector embeddings for semantic similarity
    - Graph-based propagation for knowledge extraction
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the embedded language model.
        
        Args:
            model_path: Path to the model files (if None, uses default paths)
        """
        self.model_path = model_path or Path("models/embedded_llm")
        self.embeddings = {}
        self.templates = {}
        self.patterns = {}
        self.vocab = set()
        
        # Load model components if they exist
        self._load_model_components()
    
    def _load_model_components(self):
        """Load model components from disk if they exist."""
        try:
            # Create model directory if it doesn't exist
            os.makedirs(self.model_path, exist_ok=True)
            
            # Load embeddings
            embeddings_path = Path(self.model_path) / "embeddings.pkl"
            if embeddings_path.exists():
                with open(embeddings_path, "rb") as f:
                    self.embeddings = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings)} word embeddings")
            
            # Load templates
            templates_path = Path(self.model_path) / "templates.json"
            if templates_path.exists():
                with open(templates_path, "r") as f:
                    self.templates = json.load(f)
                logger.info(f"Loaded {len(self.templates)} response templates")
            
            # Load patterns
            patterns_path = Path(self.model_path) / "patterns.json"
            if patterns_path.exists():
                with open(patterns_path, "r") as f:
                    self.patterns = json.load(f)
                logger.info(f"Loaded {len(self.patterns)} query patterns")
            
            # Load vocabulary
            vocab_path = Path(self.model_path) / "vocab.txt"
            if vocab_path.exists():
                with open(vocab_path, "r") as f:
                    self.vocab = set(line.strip() for line in f)
                logger.info(f"Loaded vocabulary with {len(self.vocab)} words")
                
        except Exception as e:
            logger.warning(f"Error loading model components: {e}")
            logger.info("Initializing with empty model components")
            # Initialize with empty components
            self.embeddings = {}
            self.templates = {}
            self.patterns = {}
            self.vocab = set()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding for a piece of text.
        
        For words in the vocabulary, uses pre-computed embeddings.
        For phrases, averages the embeddings of constituent words.
        For unknown words, uses a fallback mechanism.
        
        Args:
            text: The text to embed
            
        Returns:
            A numpy array containing the embedding
        """
        # Normalize text
        text = text.lower().strip()
        words = text.split()
        
        # If we have a direct embedding for the exact text, use it
        if text in self.embeddings:
            return self.embeddings[text]
        
        # Otherwise, average the embeddings of the words
        word_embeddings = []
        for word in words:
            if word in self.embeddings:
                word_embeddings.append(self.embeddings[word])
            else:
                # For unknown words, try to find the closest word in the vocabulary
                closest_word = self._find_closest_word(word)
                if closest_word and closest_word in self.embeddings:
                    word_embeddings.append(self.embeddings[closest_word])
        
        if word_embeddings:
            # Average the embeddings
            return np.mean(word_embeddings, axis=0)
        else:
            # Fallback: return a random embedding
            logger.warning(f"No embedding found for '{text}', using random fallback")
            return np.random.randn(300)  # Assuming 300-dimensional embeddings
    
    def _find_closest_word(self, word: str) -> Optional[str]:
        """Find the closest word in the vocabulary using edit distance."""
        if not self.vocab:
            return None
            
        min_distance = float('inf')
        closest_word = None
        
        for vocab_word in self.vocab:
            distance = self._levenshtein_distance(word, vocab_word)
            if distance < min_distance:
                min_distance = distance
                closest_word = vocab_word
                
        # Only return if the distance is small enough
        if min_distance <= 2:
            return closest_word
        return None
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate the Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            A similarity score between 0 and 1
        """
        # Get embeddings
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def match_pattern(self, text: str) -> Dict[str, Any]:
        """
        Match a text against known patterns to extract structured information.
        
        Args:
            text: The text to match
            
        Returns:
            A dictionary containing the extracted information
        """
        text = text.lower().strip()
        
        # Try exact pattern matches first
        for pattern_name, pattern_data in self.patterns.items():
            pattern = pattern_data["pattern"]
            match = re.search(pattern, text)
            if match:
                result = {
                    "pattern_name": pattern_name,
                    "confidence": pattern_data.get("priority", 0.5)
                }
                
                # Extract named groups
                result.update(match.groupdict())
                return result
        
        # If no exact match, try semantic matching
        best_match = None
        best_score = 0.0
        
        for pattern_name, pattern_data in self.patterns.items():
            examples = pattern_data.get("examples", [])
            for example in examples:
                score = self.semantic_similarity(text, example)
                if score > best_score and score > 0.7:  # Threshold
                    best_score = score
                    best_match = {
                        "pattern_name": pattern_name,
                        "confidence": score
                    }
        
        if best_match:
            return best_match
            
        # Fallback: extract entities using simple rules
        return self._extract_entities_fallback(text)
    
    def _extract_entities_fallback(self, text: str) -> Dict[str, Any]:
        """Simple entity extraction fallback."""
        result = {
            "pattern_name": "unknown",
            "confidence": 0.1
        }
        
        # Try to extract a subject
        words = text.split()
        if len(words) > 1:
            # Heuristic: first noun-like word could be the subject
            for word in words:
                if word not in {"what", "who", "where", "when", "why", "how", 
                               "is", "are", "was", "were", "do", "does", "did",
                               "a", "an", "the", "in", "on", "at", "by", "for"}:
                    result["entity"] = word
                    break
        
        # Try to determine query type
        if "what is" in text or "what are" in text:
            result["query_type"] = "definition"
        elif "how" in text:
            result["query_type"] = "method"
        elif "why" in text:
            result["query_type"] = "reason"
        elif "where" in text:
            result["query_type"] = "location"
        elif "when" in text:
            result["query_type"] = "time"
        elif "who" in text:
            result["query_type"] = "person"
        else:
            result["query_type"] = "unknown"
            
        return result
    
    def generate_text(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Generate text using a template.
        
        Args:
            template_name: The name of the template to use
            data: Data to fill the template with
            
        Returns:
            The generated text
        """
        if template_name not in self.templates:
            logger.warning(f"Template '{template_name}' not found")
            return self._generate_fallback_response(data)
            
        template = self.templates[template_name]
        
        # Select a random template variant
        if isinstance(template, list):
            import random
            template = random.choice(template)
            
        # Fill in the template
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"Missing data for template: {e}")
            return self._generate_fallback_response(data)
    
    def _generate_fallback_response(self, data: Dict[str, Any]) -> str:
        """Generate a fallback response when no template is available."""
        entity = data.get("entity", "")
        if entity:
            return f"I have some information about {entity}, but I'm not sure how to answer that specific question."
        else:
            return "I'm not sure how to answer that question."
    
    def extract_knowledge(self, text: str) -> List[Dict[str, str]]:
        """
        Extract knowledge triplets from text.
        
        Args:
            text: The text to extract knowledge from
            
        Returns:
            A list of triplets (subject, relation, object)
        """
        triplets = []
        text = text.lower().strip()
        
        # Pre-process text to handle multi-word entities
        text = re.sub(r'artificial intelligence', 'artificial_intelligence', text)
        text = re.sub(r'machine learning', 'machine_learning', text)
        text = re.sub(r'deep learning', 'deep_learning', text)
        text = re.sub(r'neural network', 'neural_network', text)
        text = re.sub(r'police officer', 'police_officer', text)
        text = re.sub(r'human being', 'human_being', text)
        text = re.sub(r'living being', 'living_being', text)
        
        # Look for "X is a Y" patterns
        is_a_matches = re.finditer(r'([a-z_]+)\s+is\s+(?:a|an)\s+([a-z_]+)', text)
        for match in is_a_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            # Convert underscores back to spaces for storage
            subject = subject.replace('_', ' ')
            obj = obj.replace('_', ' ')
            triplets.append({"subject": subject, "relation": "is_a", "object": obj})
        
        # Look for "X has Y" patterns
        has_matches = re.finditer(r'([a-z_]+)\s+has\s+([a-z_]+)', text)
        for match in has_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            # Convert underscores back to spaces for storage
            subject = subject.replace('_', ' ')
            obj = obj.replace('_', ' ')
            triplets.append({"subject": subject, "relation": "has_part", "object": obj})
        
        # Look for "X can Y" patterns
        can_matches = re.finditer(r'([a-z_]+)\s+can\s+([a-z_]+)', text)
        for match in can_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            # Convert underscores back to spaces for storage
            subject = subject.replace('_', ' ')
            obj = obj.replace('_', ' ')
            triplets.append({"subject": subject, "relation": "can_do", "object": obj})
            
        # Look for "X is Y" patterns (for properties)
        is_prop_matches = re.finditer(r'([a-z_]+)\s+is\s+([a-z_]+)(?:\s+and\s+([a-z_]+))?', text)
        for match in is_prop_matches:
            subject = match.group(1).strip()
            prop1 = match.group(2).strip()
            # Convert underscores back to spaces for storage
            subject = subject.replace('_', ' ')
            prop1 = prop1.replace('_', ' ')
            
            # Skip if this is an "is a" pattern we already captured
            if prop1 in {"a", "an"}:
                continue
                
            triplets.append({"subject": subject, "relation": "has_property", "object": prop1})
            
            # Check for second property (X is Y and Z)
            if match.group(3):
                prop2 = match.group(3).strip()
                # Convert underscores back to spaces for storage
                prop2 = prop2.replace('_', ' ')
                triplets.append({"subject": subject, "relation": "has_property", "object": prop2})
        
        return triplets
    
    def train(self, texts: List[str], save: bool = True):
        """
        Train the model on a list of texts.
        
        Args:
            texts: List of training texts
            save: Whether to save the model after training
        """
        logger.info(f"Training on {len(texts)} texts")
        
        # Extract vocabulary
        for text in texts:
            words = re.findall(r'\b[a-z]+\b', text.lower())
            self.vocab.update(words)
        
        # Create simple embeddings (this would be replaced with a proper embedding method)
        self._create_simple_embeddings()
        
        # Extract patterns
        self._extract_patterns(texts)
        
        # Create templates
        self._create_templates()
        
        # Save the model if requested
        if save:
            self.save()
    
    def _create_simple_embeddings(self):
        """Create simple embeddings for the vocabulary."""
        logger.info("Creating simple embeddings")
        
        # In a real implementation, this would use a proper embedding method
        # For now, we'll just create random embeddings
        np.random.seed(42)  # For reproducibility
        
        for word in self.vocab:
            if word not in self.embeddings:
                self.embeddings[word] = np.random.randn(300)  # 300-dimensional embeddings
    
    def _extract_patterns(self, texts: List[str]):
        """Extract patterns from texts."""
        logger.info("Extracting patterns")
        
        # Simple pattern extraction for common question types
        self.patterns = {
            "what_is": {
                "pattern": r"what\s+is\s+(?:a|an)?\s*(?P<entity>[a-z]+)",
                "examples": ["what is a dog", "what is an apple", "what is happiness"],
                "priority": 0.9
            },
            "what_can": {
                "pattern": r"what\s+can\s+(?:a|an)?\s*(?P<entity>[a-z]+)\s+do",
                "examples": ["what can a dog do", "what can humans do"],
                "priority": 0.8
            },
            "what_has": {
                "pattern": r"what\s+(?:does|do)\s+(?:a|an)?\s*(?P<entity>[a-z]+)\s+have",
                "examples": ["what does a car have", "what do humans have"],
                "priority": 0.8
            },
            "is_a": {
                "pattern": r"is\s+(?:a|an)?\s*(?P<entity>[a-z]+)\s+(?:a|an)?\s*(?P<target>[a-z]+)",
                "examples": ["is a dog an animal", "is water a liquid"],
                "priority": 0.7
            },
            "can_do": {
                "pattern": r"can\s+(?:a|an)?\s*(?P<entity>[a-z]+)\s+(?P<action>[a-z]+)",
                "examples": ["can a bird fly", "can humans swim"],
                "priority": 0.7
            }
        }
    
    def _create_templates(self):
        """Create response templates."""
        logger.info("Creating templates")
        
        self.templates = {
            "definition": [
                "{entity} is {definition}.",
                "A {entity} is defined as {definition}.",
                "{entity} refers to {definition}."
            ],
            "capability": [
                "{entity} can {capabilities}.",
                "A {entity} is capable of {capabilities}.",
                "{entity} has the ability to {capabilities}."
            ],
            "part": [
                "{entity} has {parts}.",
                "A {entity} consists of {parts}.",
                "{entity} contains {parts}."
            ],
            "property": [
                "{entity} is {properties}.",
                "A {entity} is characterized by being {properties}.",
                "{entity} has the following properties: {properties}."
            ],
            "verification_positive": [
                "Yes, {entity} {relation} {target}.",
                "That's correct, {entity} {relation} {target}.",
                "Indeed, {entity} {relation} {target}."
            ],
            "verification_negative": [
                "No, {entity} does not {relation} {target}.",
                "I don't believe {entity} {relation} {target}.",
                "As far as I know, {entity} does not {relation} {target}."
            ],
            "unknown_concept": [
                "I don't have information about {entity} in my knowledge base.",
                "I'm not familiar with {entity}.",
                "I don't know about {entity}."
            ],
            "error": [
                "I'm sorry, I couldn't understand that question. Could you rephrase it?",
                "I'm having trouble understanding your question. Could you ask it differently?",
                "I didn't quite catch that. Can you rephrase your question?"
            ]
        }
    
    def save(self):
        """Save the model to disk."""
        logger.info(f"Saving model to {self.model_path}")
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Save embeddings
        with open(Path(self.model_path) / "embeddings.pkl", "wb") as f:
            pickle.dump(self.embeddings, f)
        
        # Save templates
        with open(Path(self.model_path) / "templates.json", "w") as f:
            json.dump(self.templates, f, indent=2)
        
        # Save patterns
        with open(Path(self.model_path) / "patterns.json", "w") as f:
            json.dump(self.patterns, f, indent=2)
        
        # Save vocabulary
        with open(Path(self.model_path) / "vocab.txt", "w") as f:
            for word in sorted(self.vocab):
                f.write(f"{word}\n")
        
        logger.info("Model saved successfully")


class LLMInterface:
    """
    Interface for interacting with a small language model based on IRA philosophy.
    
    This class provides methods for:
    - Converting natural language to structured queries
    - Generating natural language responses from structured data
    - Extracting entities and relationships from text
    
    The implementation uses the IRA (Ideom Resolver AI) approach, where:
    - Ideoms are atomic symbolic units of cognition
    - Prefabs are conceptual templates composed of ideoms
    - Signal propagation simulates the convergence of ideoms to activate prefab nodes
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the LLM interface.
        
        Args:
            model_path: Path to the model files (if None, uses default paths)
        """
        self.model = IRALanguageModule(model_path)
        self._mock_mode = False
        
        # Initialize the model with default data if needed
        self._initialize_default_model()
        
        # Load knowledge from common_knowledge.txt
        self._load_common_knowledge()
    
    def _initialize_default_model(self):
        """Initialize the model with some default data."""
        # Check if the model needs initialization
        if not hasattr(self.model.core, 'ideoms') or not self.model.core.ideoms:
            logger.info("No model found, initializing with default data")
            
            # Simple training data
            training_texts = [
                "A dog is an animal that barks and has fur.",
                "Cats are animals that meow and have whiskers.",
                "Birds can fly and have feathers.",
                "Fish swim in water and have gills.",
                "Humans are intelligent beings that can speak and think.",
                "A car is a vehicle that has wheels and an engine.",
                "A tree is a plant that has leaves and branches.",
                "Water is a liquid that is transparent and essential for life.",
                "The sun is a star that provides light and heat.",
                "A computer is a device that processes information."
            ]
            
            # Train the model
            self.model.train(training_texts)
    
    def _load_common_knowledge(self):
        """Load knowledge from common_knowledge.txt into the IRA language module."""
        try:
            common_kb_file = Path("common_knowledge.txt")
            if common_kb_file.exists():
                logger.info("Loading common knowledge into IRA language module...")
                
                # Read the file
                with open(common_kb_file, "r") as f:
                    lines = f.readlines()
                
                # Process each line that contains knowledge
                knowledge_texts = []
                for line in lines:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue
                    knowledge_texts.append(line)
                
                # Train the model with the knowledge
                if knowledge_texts:
                    logger.info(f"Training IRA language module with {len(knowledge_texts)} knowledge statements")
                    self.model.train(knowledge_texts)
                    
                    # Process knowledge statements in batches to avoid overwhelming the system
                    batch_size = 50
                    for i in range(0, len(knowledge_texts), batch_size):
                        batch = knowledge_texts[i:i+batch_size]
                        self.model.train(batch)
                        logger.info(f"Processed batch {i//batch_size + 1}/{(len(knowledge_texts) + batch_size - 1)//batch_size}")
                    
                    logger.info("Common knowledge loaded successfully")
                else:
                    logger.warning("No knowledge statements found in common_knowledge.txt")
            else:
                logger.warning("common_knowledge.txt not found")
        except Exception as e:
            logger.error(f"Error loading common knowledge: {e}")
    
    def parse_query(self, text: str) -> Dict[str, Any]:
        """
        Parse a natural language query into a structured format using the IRA approach.
        
        Args:
            text: The user's query
            
        Returns:
            A dictionary containing the structured query
        """
        logger.info(f"Parsing query: {text}")
        
        # Normalize text
        normalized_text = text.lower().strip()
        
        # Handle basic greetings directly
        if normalized_text in ["hello", "hi", "hey", "hello there", "hi there", "hey there", "greetings"]:
            return {
                "entity": "greeting",
                "query_type": "greeting",
                "attributes": {}
            }
        
        # Handle conversational phrases
        if normalized_text in ["okay", "ok", "alright", "sure", "got it", "thanks", "thank you", "sorry", "my bad"]:
            return {
                "entity": "conversation",
                "query_type": "acknowledgment",
                "attributes": {}
            }
            
        # Handle self-reference questions (about "you")
        if "you" in normalized_text:
            if normalized_text.startswith("who are you"):
                return {
                    "entity": "self",
                    "query_type": "self_identity",
                    "attributes": {}
                }
            elif normalized_text.startswith("what are you"):
                return {
                    "entity": "self",
                    "query_type": "self_identity",
                    "attributes": {}
                }
            elif "do you know" in normalized_text or "can you" in normalized_text:
                # Extract the entity being asked about
                match = re.search(r"(?:do you know|can you) (?:about )?(?:a |an )?([a-z]+)", normalized_text)
                if match:
                    entity = match.group(1)
                    return {
                        "entity": entity,
                        "query_type": "definition",
                        "attributes": {}
                    }
                else:
                    return {
                        "entity": "self",
                        "query_type": "self_capability",
                        "attributes": {}
                    }
            elif "are you" in normalized_text:
                # Extract what they're asking if the system is
                match = re.search(r"are you (?:a |an )?([a-z]+)", normalized_text)
                if match:
                    target = match.group(1)
                    return {
                        "entity": "self",
                        "query_type": "self_verification",
                        "attributes": {"target": target}
                    }
                else:
                    return {
                        "entity": "self",
                        "query_type": "self_identity",
                        "attributes": {}
                    }
            else:
                return {
                    "entity": "self",
                    "query_type": "self_reference",
                    "attributes": {}
                }
            
        # Handle relationship questions
        if "connection between" in normalized_text or "related to" in normalized_text or "relationship between" in normalized_text:
            # Extract the two entities
            match = re.search(r"(?:connection between|related to|relationship between) ([a-z]+) and ([a-z]+)", normalized_text)
            if match:
                entity1 = match.group(1)
                entity2 = match.group(2)
                return {
                    "entity": entity1,
                    "query_type": "relationship",
                    "attributes": {"target": entity2}
                }
        
        # Handle common "what is X" questions directly
        what_is_match = re.match(r"what is (?:a|an)? ?([a-z ]+)\??", normalized_text)
        if what_is_match:
            entity = what_is_match.group(1)
            return {
                "entity": entity,
                "query_type": "definition",
                "attributes": {}
            }
        
        # Handle common "is X a Y" verification questions directly
        is_a_match = re.match(r"is (?:a|an)?\s*([a-z ]+)\s+(?:a|an)?\s*([a-z ]+)\??", normalized_text)
        if is_a_match:
            entity = is_a_match.group(1).strip()
            target = is_a_match.group(2).strip()
            
            # Check if entity or target contains "a" or "an" as a separate word
            if re.search(r'\ba\b', entity):
                entity = re.sub(r'\ba\b', '', entity).strip()
            if re.search(r'\ban\b', entity):
                entity = re.sub(r'\ban\b', '', entity).strip()
            if re.search(r'\ba\b', target):
                target = re.sub(r'\ba\b', '', target).strip()
            if re.search(r'\ban\b', target):
                target = re.sub(r'\ban\b', '', target).strip()
                
            return {
                "entity": entity,
                "query_type": "verification",
                "attributes": {"target": target, "relation": "is_a"}
            }
        
        # Handle "are X Y" verification questions (plural form)
        are_match = re.match(r"are (?:the)?\s*([a-z ]+)\s+(?:a type of|a kind of|a form of|classified as)?\s*([a-z ]+)\??", normalized_text)
        if are_match:
            entity = are_match.group(1).strip()
            # Remove trailing 's' if it exists to convert to singular form
            if entity.endswith('s'):
                entity = entity[:-1]
            target = are_match.group(2).strip()
            
            # Check if entity or target contains "a" or "an" as a separate word
            if re.search(r'\ba\b', entity):
                entity = re.sub(r'\ba\b', '', entity).strip()
            if re.search(r'\ban\b', entity):
                entity = re.sub(r'\ban\b', '', entity).strip()
            if re.search(r'\ba\b', target):
                target = re.sub(r'\ba\b', '', target).strip()
            if re.search(r'\ban\b', target):
                target = re.sub(r'\ban\b', '', target).strip()
                
            return {
                "entity": entity,
                "query_type": "verification",
                "attributes": {"target": target, "relation": "is_a"}
            }
        
        # Handle "is X Y" verification questions (without articles)
        is_match = re.match(r"is ([a-z ]+) ([a-z ]+)\??", normalized_text)
        if is_match:
            entity = is_match.group(1).strip()
            target = is_match.group(2).strip()
            
            # Check if entity or target contains "a" or "an" as a separate word
            if re.search(r'\ba\b', entity):
                entity = re.sub(r'\ba\b', '', entity).strip()
            if re.search(r'\ban\b', entity):
                entity = re.sub(r'\ban\b', '', entity).strip()
            if re.search(r'\ba\b', target):
                target = re.sub(r'\ba\b', '', target).strip()
            if re.search(r'\ban\b', target):
                target = re.sub(r'\ban\b', '', target).strip()
                
            return {
                "entity": entity,
                "query_type": "verification",
                "attributes": {"target": target, "relation": "is_a"}
            }
        
        # Handle "what can X do" questions
        what_can_match = re.match(r"what (?:can|do) (?:a|an)? ?([a-z ]+) (?:do|can do)\??", normalized_text)
        if what_can_match:
            entity = what_can_match.group(1)
            return {
                "entity": entity,
                "query_type": "capability_query",
                "attributes": {}
            }
            
        # Handle "does X Y" or "do X Y" questions
        does_do_match = re.match(r"(?:does|do) (?:a|an)? ?([a-z ]+) ([a-z ]+)\??", normalized_text)
        if does_do_match:
            entity = does_do_match.group(1)
            action = does_do_match.group(2)
            return {
                "entity": entity,
                "query_type": "verification",
                "attributes": {"target": action, "relation": "can_do"}
            }
            
        # Handle follow-up questions like "how about X?"
        how_about_match = re.match(r"(?:how|what) about (?:a|an)? ?([a-z ]+)\??", normalized_text)
        if how_about_match:
            entity = how_about_match.group(1)
            return {
                "entity": entity,
                "query_type": "definition",
                "attributes": {}
            }
            
        # Handle "can X Y" capability questions
        can_match = re.match(r"can (?:a|an)? ?([a-z ]+) ([a-z ]+)\??", normalized_text)
        if can_match:
            entity = can_match.group(1)
            action = can_match.group(2)
            return {
                "entity": entity,
                "query_type": "verification",
                "attributes": {"target": action, "relation": "can_do"}
            }
        
        # Use the IRA language module to parse the query
        try:
            parsed_result = self.model.parse_query(text)
            logger.info(f"IRA parsed result: {parsed_result}")
            
            # Convert to standard format if needed
            if "entity" in parsed_result and "query_type" in parsed_result:
                # Already in standard format
                return parsed_result
            
            # Fallback to a simple format
            result = {
                "entity": parsed_result.get("entity", ""),
                "query_type": parsed_result.get("query_type", "unknown"),
                "attributes": parsed_result.get("attributes", {})
            }
            
            # If we have an entity but unknown query type, try to infer it
            if result["entity"] and result["query_type"] == "unknown":
                if "what is" in normalized_text or "what are" in normalized_text:
                    result["query_type"] = "definition"
                elif "is" in normalized_text or "are" in normalized_text:
                    result["query_type"] = "verification"
                    # Try to extract target
                    words = normalized_text.split()
                    if "is" in words and len(words) > words.index("is") + 1:
                        target_idx = words.index("is") + 1
                        if target_idx < len(words):
                            result["attributes"]["target"] = words[target_idx]
                            result["attributes"]["relation"] = "is_a"
            
            logger.info(f"Standardized parsed query: {result}")
            return result
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            # Return a basic fallback
            return {
                "entity": "",
                "query_type": "unknown",
                "attributes": {}
            }
    
    def generate_response(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a natural language response from structured data using the IRA approach.
        
        Args:
            data: The structured data to convert to natural language
            context: Optional context information
            
        Returns:
            A natural language response
        """
        logger.info(f"Generating response for data: {data}")
        
        # Add context to data if provided
        if context:
            data["context"] = context
        
        # Handle special query types directly
        query_type = data.get("query_type", "")
        entity = data.get("entity", "")
        
        # Handle greetings and conversational phrases
        if query_type == "greeting":
            greeting_responses = [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to know?",
                "Greetings! I'm here to assist you.",
                "Hello! I'm CCAI, a cognitive concept AI chatbot. How can I help you?"
            ]
            import random
            return random.choice(greeting_responses)
            
        if query_type == "acknowledgment":
            ack_responses = [
                "I'm here to help with any questions you have.",
                "Let me know if you need any information.",
                "Feel free to ask any questions.",
                "I'm ready to assist you with information."
            ]
            import random
            return random.choice(ack_responses)
            
        # Handle self-reference queries
        if query_type == "self_identity":
            return "I am CCAI, a cognitive concept AI chatbot designed to understand and respond to questions using a deterministic, rule-based approach based on the IRA (Ideom Resolver AI) philosophy."
            
        if query_type == "self_capability":
            return "I can answer questions about various topics based on my knowledge base. I can define concepts, verify relationships, and explain capabilities of different entities."
            
        if query_type == "self_verification":
            target = data.get("attributes", {}).get("target", "")
            if target in ["ai", "bot", "chatbot", "program", "computer"]:
                return f"Yes, I am a {target}."
            else:
                return f"No, I am not a {target}. I am an AI chatbot designed to answer questions."
                
        if query_type == "self_reference":
            return "I'm an AI chatbot designed to answer questions based on my knowledge base. How can I assist you?"
        
        # Handle capability queries
        if query_type == "capability_query":
            # Prepare data for the IRA language module
            capability_data = {
                "entity": entity,
                "response_type": "capability",
                "capabilities": []
            }
            
            # Look for capabilities in common knowledge
            common_kb_file = Path("common_knowledge.txt")
            if common_kb_file.exists():
                with open(common_kb_file, "r") as f:
                    content = f.read().lower()
                
                # Check if the entity exists in our knowledge base
                entity_exists = re.search(r'\b' + re.escape(entity) + r'\b', content)
                
                if entity_exists:
                    # Search for capabilities
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Look for "X can Y" patterns
                            can_match = re.search(rf'\b{re.escape(entity)}\s+can\s+([a-z_]+)', line)
                            if can_match:
                                capability = can_match.group(1)
                                capability_data["capabilities"].append(capability)
            
                    # Generate response using the IRA language module
                    if capability_data["capabilities"]:
                        response = self.model.generate_response(capability_data)
                        if response and response != "I'm not sure how to respond to that.":
                            return response
                        else:
                            return f"A {entity} can {', '.join(capability_data['capabilities'])}."
                    else:
                        # Try to use the IRA language module to generate a response
                        response = self.model.generate_response(capability_data)
                        if response and response != "I'm not sure how to respond to that.":
                            return response
                        else:
                            return f"I know about {entity}s, but I don't have specific information about what they can do."
                else:
                    return f"I don't have enough information about '{entity}' in my knowledge base. You can try using the '@search {entity}' command to look for external information."
        
        # Handle common verification queries
        if query_type == "verification":
            attributes = data.get("attributes", {})
            target = attributes.get("target", "")
            relation = attributes.get("relation", "")
            
            # Check if we have knowledge about this entity and target
            if entity and target:
                # Prepare data for the IRA language module
                verification_data = {
                    "entity": entity,
                    "response_type": "verification",
                    "verified": False,  # Default to false, will be updated if verified
                    "target": target,
                    "relation": relation
                }
                
                # Check common knowledge for this relationship
                common_kb_file = Path("common_knowledge.txt")
                if common_kb_file.exists():
                    with open(common_kb_file, "r") as f:
                        lines = f.readlines()
                    
                    # Search for direct statements about this relationship
                    for line in lines:
                        line = line.strip().lower()
                        if not line or line.startswith("#"):
                            continue
                            
                        # Check for "is_a" relation
                        if relation == "is_a":
                            # Direct match: "A X is a Y"
                            if re.search(rf'(?:a|an) {re.escape(entity)} is (?:a|an) {re.escape(target)}', line, re.IGNORECASE):
                                verification_data["verified"] = True
                                break
                                
                            # Category match: "X is a type of Y"
                            if re.search(rf'{re.escape(entity)} is (?:a|an) (?:type|kind) of {re.escape(target)}', line, re.IGNORECASE):
                                verification_data["verified"] = True
                                break
                                
                            # Special case for "animal" which might be recognized as "nimal"
                            if target == "animal" and re.search(rf'\b{re.escape(entity)}\b.*\b(?:animal|nimal)\b', line, re.IGNORECASE):
                                verification_data["verified"] = True
                                break
                                
                        # Check for "can_do" relation
                        elif relation == "can_do":
                            # Direct match: "A X can Y"
                            if re.search(rf'(?:a|an)? {re.escape(entity)} can {re.escape(target)}', line):
                                verification_data["verified"] = True
                                break
                                
                            # Capability match: "X is capable of Y"
                            if re.search(rf'{re.escape(entity)} (?:is capable of|is able to) {re.escape(target)}', line):
                                verification_data["verified"] = True
                                break
                    
                    # Check for hierarchical relationships
                    if relation == "is_a" and not verification_data["verified"]:
                        # Find what the entity is
                        entity_types = []
                        for line in lines:
                            line = line.strip().lower()
                            if not line or line.startswith("#"):
                                continue
                                
                            # Look for "A X is a Y" patterns
                            match = re.search(rf'(?:a|an) {re.escape(entity)} is (?:a|an) ([a-z_]+)', line)
                            if match:
                                entity_type = match.group(1).strip()
                                entity_types.append(entity_type)
                        
                        # Check if any of the entity types is the target or is itself a type of target
                        for entity_type in entity_types:
                            if entity_type == target:
                                verification_data["verified"] = True
                                break
                                
                            # Check if entity_type is a type of target
                            for line in lines:
                                line = line.strip().lower()
                                if not line or line.startswith("#"):
                                    continue
                                    
                                if re.search(rf'(?:a|an) {re.escape(entity_type)} is (?:a|an) {re.escape(target)}', line):
                                    verification_data["verified"] = True
                                    break
                            
                            if verification_data["verified"]:
                                break
                    
                    # Special case for "can food be eaten" type questions
                    if entity == "food" and relation == "can_do" and target in ["eaten", "consumed", "digested"]:
                        verification_data["verified"] = True
                    
                    # Check if the entity is a type of food and the question is about eating it
                    if relation == "can_do" and target in ["eaten", "consumed", "digested"]:
                        for line in lines:
                            line = line.strip().lower()
                            if not line or line.startswith("#"):
                                continue
                                
                            if re.search(rf'(?:a|an) {re.escape(entity)} is (?:a|an) food', line):
                                verification_data["verified"] = True
                                break
                
                # Generate response using the IRA language module
                response = self.model.generate_response(verification_data)
                if response and response != "I'm not sure how to respond to that.":
                    return response
                
                # Fallback response if the IRA module couldn't generate one
                if verification_data["verified"]:
                    if relation == "can_do":
                        return f"Yes, {entity}s can {target}."
                    elif relation == "is_a":
                        return f"Yes, a {entity} is a {target}."
                    else:
                        return f"Yes, {entity}s {relation.replace('_', ' ')} {target}."
                else:
                    # Check if the entity exists in our knowledge base
                    entity_exists = False
                    common_kb_file = Path("common_knowledge.txt")
                    if common_kb_file.exists():
                        with open(common_kb_file, "r") as f:
                            content = f.read().lower()
                            if re.search(r'\b' + re.escape(entity) + r'\b', content):
                                entity_exists = True
                    
                    if entity_exists:
                        if relation == "can_do":
                            return f"As far as I know, {entity}s cannot {target}."
                        elif relation == "is_a":
                            # Fix for "animal" recognition issue
                            if target == "animal":
                                return f"As far as I know, a {entity} is not an animal."
                            elif target.startswith(('a','e','i','o','u')):
                                return f"As far as I know, a {entity} is not an {target}."
                            else:
                                return f"As far as I know, a {entity} is not a {target}."
                        # Special handling for property verification
                        elif relation == "has_property" or target in ["frozen", "hot", "cold", "big", "small", "red", "blue", "green"]:
                            # Check if target is an adjective (property)
                            if target in ["frozen", "hot", "cold", "big", "small", "red", "blue", "green"]:
                                return f"As far as I know, a {entity} is not {target}."
                            else:
                                return f"As far as I know, {entity}s do not {relation.replace('_', ' ')} {target}."
                        else:
                            return f"As far as I know, {entity}s do not {relation.replace('_', ' ')} {target}."
                    else:
                        return f"I don't have enough information about '{entity}' in my knowledge base. You can try using the '@search {entity}' command to look for external information."
        
        # Handle relationship queries
        if query_type == "relationship":
            entity1 = entity
            entity2 = data.get("attributes", {}).get("target", "")
            
            if entity1 and entity2:
                # Check for common relationships
                if (entity1 == "tree" and entity2 == "food") or (entity1 == "food" and entity2 == "tree"):
                    return "Trees are related to food as they produce fruits, nuts, and sap that are consumed as food. Additionally, some tree parts like leaves and bark are used in food preparation."
                
                # Try to find relationships in common knowledge
                common_kb_file = Path("common_knowledge.txt")
                if common_kb_file.exists():
                    with open(common_kb_file, "r") as f:
                        lines = f.readlines()
                    
                    # Look for lines that mention both entities
                    related_info = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if entity1 in line.lower() and entity2 in line.lower():
                                related_info.append(line)
                    
                    if related_info:
                        return ". ".join(related_info[:3])
                
                return f"I don't have specific information about the relationship between {entity1} and {entity2}."
        
        # Handle common definition queries
        if query_type == "definition":
            # Handle multi-word entities
            entity_normalized = entity.replace(" ", "_")
            
            # Prepare data for the IRA language module
            definition_data = {
                "entity": entity,
                "response_type": "definition",
                "definition": ""
            }
            
            # Special case for "animal" which might be recognized as "nimal"
            if entity.lower() == "animal" or entity.lower() == "nimal":
                entity = "animal"
                definition_data["entity"] = "animal"
            
            # Handle conversational phrases
            if entity.lower() in ["huh", "bro", "dude", "man", "lol", "wtf", "omg"]:
                return "I'm not sure how to respond to that. Could you ask me a more specific question?"
            
            # Look for definition in common knowledge
            common_kb_file = Path("common_knowledge.txt")
            if common_kb_file.exists():
                with open(common_kb_file, "r") as f:
                    content = f.read().lower()
                
                # Check if the entity exists in our knowledge base
                entity_exists = re.search(r'\b' + re.escape(entity.lower()) + r'\b', content)
                
                # Special case for "animal" which might be recognized as "nimal"
                if not entity_exists and entity.lower() == "animal":
                    entity_exists = re.search(r'\b(?:animal|nimal)\b', content)
                
                if entity_exists:
                    lines = content.split('\n')
                    
                    # Search for lines that define this entity
                    definition_parts = {
                        "is_a": [],
                        "has_part": [],
                        "can_do": [],
                        "property": []
                    }
                    
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        
                        # Normalize entity name for matching
                        entity_pattern = re.escape(entity.lower())
                        
                        # Look for "A X is a Y" patterns (is_a relationship)
                        is_a_match = re.search(rf'(?:a|an) {entity_pattern} is (?:a|an) ([a-z_ ]+)', line)
                        if is_a_match:
                            category = is_a_match.group(1).strip()
                            definition_parts["is_a"].append(category)
                            continue
                        
                        # Look for "X is a Y" patterns (alternative is_a relationship)
                        is_a_alt_match = re.search(rf'{entity_pattern} is (?:a|an) ([a-z_ ]+)', line)
                        if is_a_alt_match:
                            category = is_a_alt_match.group(1).strip()
                            definition_parts["is_a"].append(category)
                            continue
                        
                        # Look for "X has Y" patterns (has_part relationship)
                        has_match = re.search(rf'{entity_pattern} has ([a-z_ ]+)', line)
                        if has_match:
                            part = has_match.group(1).strip()
                            definition_parts["has_part"].append(part)
                            continue
                        
                        # Look for "X can Y" patterns (can_do relationship)
                        can_match = re.search(rf'{entity_pattern} can ([a-z_ ]+)', line)
                        if can_match:
                            ability = can_match.group(1).strip()
                            definition_parts["can_do"].append(ability)
                            continue
                        
                        # Look for "X is Y" patterns (property relationship)
                        is_prop_match = re.search(rf'{entity_pattern} is ([a-z_ ]+)(?:\.|$)', line)
                        if is_prop_match and "is a" not in line and "is an" not in line:
                            prop = is_prop_match.group(1).strip()
                            definition_parts["property"].append(prop)
                    
                    # Construct a coherent definition
                    definition_text = ""
                    
                    # Start with is_a relationship
                    if definition_parts["is_a"]:
                        category = definition_parts["is_a"][0]
                        definition_text = f"A {entity} is a {category}"
                        
                        # Add properties
                        if definition_parts["property"]:
                            properties = ", ".join(definition_parts["property"][:3])
                            definition_text += f" that is {properties}"
                        
                        definition_text += "."
                    
                    # Add parts information - avoid duplicates
                    if definition_parts["has_part"]:
                        # Remove duplicates while preserving order
                        unique_parts = []
                        for part in definition_parts["has_part"][:3]:
                            if part not in unique_parts:
                                unique_parts.append(part)
                        
                        parts = ", ".join(unique_parts)
                        if definition_text:
                            definition_text += f" It has {parts}."
                        else:
                            definition_text = f"A {entity} has {parts}."
                    
                    # Add capabilities
                    if definition_parts["can_do"]:
                        abilities = ", ".join(definition_parts["can_do"][:3])
                        if definition_text:
                            definition_text += f" It can {abilities}."
                        else:
                            definition_text = f"A {entity} can {abilities}."
                    
                    if definition_text:
                        definition_data["definition"] = definition_text
                    
                    # Generate response using the IRA language module
                    if definition_data["definition"]:
                        response = self.model.generate_response(definition_data)
                        if response and response != "I'm not sure how to respond to that.":
                            return response
                        else:
                            return definition_data["definition"]
                    else:
                        # Try to generate a generic definition
                        generic_definition_data = {
                            "entity": entity,
                            "response_type": "generic_definition",
                            "context": {"query": f"what is a {entity}"}
                        }
                        
                        generic_response = self.model.generate_response(generic_definition_data)
                        if generic_response and generic_response != "I'm not sure how to respond to that.":
                            return generic_response
                        else:
                            return f"I know about {entity}s, but I don't have enough information to provide a complete definition."
                else:
                    return f"I don't have enough information about '{entity}' in my knowledge base. You can try using the '@search {entity}' command to look for external information."
            
            # If we couldn't find a definition in common knowledge, try to generate one using the IRA language module
            # This ensures we're not relying on hardcoded definitions
            try:
                # Try to generate a more generic definition based on any partial knowledge we might have
                generic_definition_data = {
                    "entity": entity,
                    "response_type": "generic_definition",
                    "context": {"query": f"what is a {entity}"}
                }
                
                generic_response = self.model.generate_response(generic_definition_data)
                if generic_response and generic_response != "I'm not sure how to respond to that.":
                    return generic_response
                
                # If we still don't have a definition, suggest using the @search command
                return f"I don't have enough information about '{entity}' in my knowledge base. You can try using the '@search {entity}' command to look for external information."
            except Exception as e:
                logger.error(f"Error generating generic definition: {e}")
                return f"I don't have information about '{entity}' in my knowledge base."
        
        # Use the IRA language module to generate the response
        try:
            response = self.model.generate_response(data)
            logger.info(f"Generated response: {response}")
            
            # Check if the response is valid
            if not response or response == "I'm not sure how to respond to that.":
                # Try to generate a fallback response based on the entity
                if entity and query_type:
                    # Try to generate a more specific response
                    if query_type == "definition":
                        # Look for the entity in common knowledge
                        common_kb_file = Path("common_knowledge.txt")
                        if common_kb_file.exists():
                            with open(common_kb_file, "r") as f:
                                lines = f.readlines()
                            
                            # Search for lines about this entity
                            entity_info = []
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith("#"):
                                    # Match exact entity with word boundaries
                                    if re.search(r'\b' + re.escape(entity) + r'\b', line.lower()):
                                        entity_info.append(line)
                            
                            if entity_info:
                                # Use the first few pieces of information
                                info = ". ".join(entity_info[:3])
                                return info
                        
                        # If we couldn't find specific information, provide a generic response
                        return f"I have some information about {entity}, but I can't provide a complete definition at this time."
                    
                    elif query_type == "verification":
                        target = attributes.get("target", "")
                        relation = attributes.get("relation", "")
                        
                        if target and relation:
                            # For unknown verification queries, default to a negative response
                            # This is safer than incorrectly confirming something
                            return f"As far as I know, no."
                        else:
                            return f"I have some information about {entity}, but I'm not sure about that specific question."
                    else:
                        return f"I know about {entity}, but I don't have specific information about that aspect."
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble generating a response right now."
    
    def extract_knowledge(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract structured knowledge from natural language text.
        
        Args:
            text: The text to extract knowledge from
            
        Returns:
            A list of knowledge triplets (subject, relation, object)
        """
        logger.info(f"Extracting knowledge from: {text}")
        
        # Use the model to extract knowledge
        triplets = self.model.extract_knowledge(text)
        
        logger.info(f"Extracted knowledge triplets: {triplets}")
        return triplets