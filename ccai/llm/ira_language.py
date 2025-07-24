"""
IRA Language Module for CCAI chatbot.

This module implements a custom language understanding and generation system
based on the IRA (Ideom Resolver AI) philosophy, where:
- Ideoms are atomic symbolic units of cognition
- Prefabs are conceptual templates composed of ideoms
- Signal propagation simulates the convergence of ideoms to activate prefab nodes
"""

import os
import logging
import json
import re
import time
import random
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from pathlib import Path
import numpy as np
import pickle
from collections import defaultdict, Counter

# Set up logging
logger = logging.getLogger(__name__)

class Ideom:
    """
    An atomic symbolic unit of cognition in the IRA philosophy.
    
    Ideoms are the fundamental building blocks of knowledge and language,
    representing atomic concepts that can be combined to form more complex
    structures.
    """
    
    def __init__(self, name: str, category: str = "entity"):
        """
        Initialize an ideom.
        
        Args:
            name: The name of the ideom
            category: The category of the ideom (entity, action, property, etc.)
        """
        self.name = name
        self.category = category
        self.activation = 0.0
        self.connections: Dict[str, float] = {}  # Connected ideoms and their weights
        self.properties: Dict[str, Any] = {}
    
    def connect(self, other_ideom: str, weight: float = 1.0):
        """Connect this ideom to another with a specified weight."""
        self.connections[other_ideom] = weight
    
    def activate(self, strength: float = 1.0):
        """Activate this ideom with a specified strength."""
        self.activation = min(1.0, self.activation + strength)
    
    def decay(self, rate: float = 0.1):
        """Decay the activation of this ideom."""
        self.activation = max(0.0, self.activation - rate)
    
    def reset(self):
        """Reset the activation to zero."""
        self.activation = 0.0
    
    def __repr__(self):
        return f"Ideom({self.name}, {self.category}, activation={self.activation:.2f})"


class Prefab:
    """
    A conceptual template composed of ideoms in the IRA philosophy.
    
    Prefabs represent recognizable patterns or concepts that emerge from
    the combination of ideoms. They are activated when their constituent
    ideoms are activated in the right pattern.
    """
    
    def __init__(self, name: str, pattern: Dict[str, float], category: str = "template"):
        """
        Initialize a prefab.
        
        Args:
            name: The name of the prefab
            pattern: A dictionary mapping ideom names to their required activation weights
            category: The category of the prefab
        """
        self.name = name
        self.pattern = pattern
        self.category = category
        self.activation = 0.0
        self.threshold = 0.15  # Even lower activation threshold for easier activation
    
    def compute_activation(self, ideoms: Dict[str, Ideom]) -> float:
        """
        Compute the activation level of this prefab based on the activation of its ideoms.
        
        Args:
            ideoms: A dictionary of ideoms and their current state
            
        Returns:
            The activation level (0.0 to 1.0)
        """
        total_weight = sum(self.pattern.values())
        weighted_sum = 0.0
        
        for ideom_name, required_weight in self.pattern.items():
            if ideom_name in ideoms:
                weighted_sum += ideoms[ideom_name].activation * required_weight
        
        self.activation = weighted_sum / total_weight if total_weight > 0 else 0.0
        return self.activation
    
    def is_activated(self) -> bool:
        """Check if this prefab is activated (above threshold)."""
        return self.activation >= self.threshold
    
    def reset(self):
        """Reset the activation to zero."""
        self.activation = 0.0
    
    def __repr__(self):
        return f"Prefab({self.name}, {self.category}, activation={self.activation:.2f})"


class IRALanguageCore:
    """
    Core implementation of the IRA language understanding and generation system.
    
    This class manages ideoms and prefabs, and implements the signal propagation
    mechanism that simulates the convergence of ideoms to activate prefab nodes.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the IRA language core.
        
        Args:
            model_path: Path to the model files (if None, uses default paths)
        """
        self.model_path = model_path or Path("models/ira_language")
        self.ideoms: Dict[str, Ideom] = {}
        self.prefabs: Dict[str, Prefab] = {}
        self.word_to_ideoms: Dict[str, List[str]] = defaultdict(list)
        self.category_to_ideoms: Dict[str, List[str]] = defaultdict(list)
        self.category_to_prefabs: Dict[str, List[str]] = defaultdict(list)
        
        # Load model components if they exist
        self._load_model_components()
    
    def _load_model_components(self):
        """Load model components from disk if they exist."""
        try:
            # Create model directory if it doesn't exist
            os.makedirs(self.model_path, exist_ok=True)
            
            # Load ideoms
            ideoms_path = Path(self.model_path) / "ideoms.pkl"
            if ideoms_path.exists():
                with open(ideoms_path, "rb") as f:
                    self.ideoms = pickle.load(f)
                logger.info(f"Loaded {len(self.ideoms)} ideoms")
                
                # Rebuild indices
                self.word_to_ideoms = defaultdict(list)
                self.category_to_ideoms = defaultdict(list)
                for ideom_name, ideom in self.ideoms.items():
                    self.word_to_ideoms[ideom_name].append(ideom_name)
                    self.category_to_ideoms[ideom.category].append(ideom_name)
            
            # Load prefabs
            prefabs_path = Path(self.model_path) / "prefabs.pkl"
            if prefabs_path.exists():
                with open(prefabs_path, "rb") as f:
                    self.prefabs = pickle.load(f)
                logger.info(f"Loaded {len(self.prefabs)} prefabs")
                
                # Rebuild indices
                self.category_to_prefabs = defaultdict(list)
                for prefab_name, prefab in self.prefabs.items():
                    self.category_to_prefabs[prefab.category].append(prefab_name)
                
        except Exception as e:
            logger.warning(f"Error loading model components: {e}")
            logger.info("Initializing with empty model components")
            # Initialize with empty components
            self.ideoms = {}
            self.prefabs = {}
            self.word_to_ideoms = defaultdict(list)
            self.category_to_ideoms = defaultdict(list)
            self.category_to_prefabs = defaultdict(list)
    
    def add_ideom(self, name: str, category: str = "entity") -> Ideom:
        """
        Add a new ideom to the system.
        
        Args:
            name: The name of the ideom
            category: The category of the ideom
            
        Returns:
            The created ideom
        """
        if name in self.ideoms:
            return self.ideoms[name]
            
        ideom = Ideom(name, category)
        self.ideoms[name] = ideom
        self.word_to_ideoms[name].append(name)
        self.category_to_ideoms[category].append(name)
        return ideom
    
    def add_prefab(self, name: str, pattern: Dict[str, float], category: str = "template") -> Prefab:
        """
        Add a new prefab to the system.
        
        Args:
            name: The name of the prefab
            pattern: A dictionary mapping ideom names to their required activation weights
            category: The category of the prefab
            
        Returns:
            The created prefab
        """
        if name in self.prefabs:
            return self.prefabs[name]
            
        # Create any ideoms that don't exist yet
        for ideom_name in pattern.keys():
            if ideom_name not in self.ideoms:
                self.add_ideom(ideom_name)
        
        prefab = Prefab(name, pattern, category)
        self.prefabs[name] = prefab
        self.category_to_prefabs[category].append(name)
        return prefab
    
    def reset_activations(self):
        """Reset all ideom and prefab activations."""
        for ideom in self.ideoms.values():
            ideom.reset()
            
        for prefab in self.prefabs.values():
            prefab.reset()
    
    def activate_ideoms(self, text: str, strength: float = 1.0) -> List[str]:
        """
        Activate ideoms based on words in the text.
        
        Args:
            text: The input text
            strength: The activation strength
            
        Returns:
            List of activated ideom names
        """
        # Normalize and pre-process text for multi-word entities
        text = text.lower().strip()
        
        # Replace common multi-word phrases with single tokens
        text = re.sub(r'artificial intelligence', 'artificial_intelligence', text)
        text = re.sub(r'machine learning', 'machine_learning', text)
        text = re.sub(r'deep learning', 'deep_learning', text)
        text = re.sub(r'neural network', 'neural_network', text)
        text = re.sub(r'police officer', 'police_officer', text)
        text = re.sub(r'human being', 'human_being', text)
        text = re.sub(r'living being', 'living_being', text)
        
        # Tokenize text
        words = re.findall(r'\b[a-z_]+\b', text)
        
        # Activate ideoms directly corresponding to words
        activated = []
        for word in words:
            # Check for the word itself
            for ideom_name in self.word_to_ideoms.get(word, []):
                self.ideoms[ideom_name].activate(strength)
                activated.append(ideom_name)
            
            # Also check for the word with underscores replaced by spaces
            # This helps with multi-word entities
            if '_' in word:
                spaced_word = word.replace('_', ' ')
                for ideom_name in self.word_to_ideoms.get(spaced_word, []):
                    self.ideoms[ideom_name].activate(strength)
                    activated.append(ideom_name)
        
        return activated
    
    def propagate_activation(self, iterations: int = 3, decay_rate: float = 0.1) -> Dict[str, float]:
        """
        Propagate activation through the ideom network.
        
        Args:
            iterations: Number of propagation iterations
            decay_rate: Rate at which activation decays
            
        Returns:
            Dictionary of prefab names and their activation levels
        """
        # Propagate activation for specified iterations
        for _ in range(iterations):
            # Store current activations to avoid immediate feedback
            current_activations = {name: ideom.activation for name, ideom in self.ideoms.items()}
            
            # Propagate activation to connected ideoms
            for ideom_name, ideom in self.ideoms.items():
                for connected_name, weight in ideom.connections.items():
                    if connected_name in self.ideoms:
                        propagated_activation = current_activations[ideom_name] * weight
                        self.ideoms[connected_name].activate(propagated_activation)
            
            # Apply decay
            for ideom in self.ideoms.values():
                ideom.decay(decay_rate)
        
        # Compute prefab activations
        prefab_activations = {}
        for prefab_name, prefab in self.prefabs.items():
            activation = prefab.compute_activation(self.ideoms)
            prefab_activations[prefab_name] = activation
        
        return prefab_activations
    
    def get_activated_prefabs(self, threshold: float = 0.5) -> List[str]:
        """
        Get the names of prefabs that are activated above the threshold.
        
        Args:
            threshold: Activation threshold
            
        Returns:
            List of activated prefab names
        """
        return [name for name, prefab in self.prefabs.items() 
                if prefab.activation >= threshold]
    
    def process_text(self, text: str, iterations: int = 3) -> Dict[str, Any]:
        """
        Process text through the IRA language system.
        
        Args:
            text: The input text
            iterations: Number of propagation iterations
            
        Returns:
            A dictionary containing the processing results
        """
        # Reset all activations
        self.reset_activations()
        
        # Activate ideoms based on text
        activated_ideoms = self.activate_ideoms(text)
        
        # Propagate activation
        prefab_activations = self.propagate_activation(iterations)
        
        # Get activated prefabs
        activated_prefabs = self.get_activated_prefabs()
        
        # Return results
        return {
            "activated_ideoms": activated_ideoms,
            "prefab_activations": prefab_activations,
            "activated_prefabs": activated_prefabs
        }
    
    def save(self):
        """Save the model to disk."""
        logger.info(f"Saving model to {self.model_path}")
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Save ideoms
        with open(Path(self.model_path) / "ideoms.pkl", "wb") as f:
            pickle.dump(self.ideoms, f)
        
        # Save prefabs
        with open(Path(self.model_path) / "prefabs.pkl", "wb") as f:
            pickle.dump(self.prefabs, f)
        
        logger.info("Model saved successfully")


class IRALanguageUnderstanding:
    """
    Language understanding module based on the IRA philosophy.
    
    This class uses the IRA language core to understand natural language
    by activating ideoms and prefabs, and extracting structured information.
    """
    
    def __init__(self, core: Optional[IRALanguageCore] = None):
        """
        Initialize the language understanding module.
        
        Args:
            core: The IRA language core (created if None)
        """
        self.core = core or IRALanguageCore()
        self.query_prefabs: Dict[str, Dict[str, Any]] = {}
        
        # Initialize query prefabs if needed
        if not self.core.prefabs:
            self._initialize_query_prefabs()
    
    def _initialize_query_prefabs(self):
        """Initialize prefabs for common query types."""
        # Definition query prefab
        self.core.add_prefab(
            "definition_query",
            {
                "what": 1.0,
                "is": 1.0,
                "definition": 0.8,
                "meaning": 0.8,
                "describe": 0.8
            },
            category="query"
        )
        
        # Capability query prefab
        self.core.add_prefab(
            "capability_query",
            {
                "what": 0.8,
                "can": 1.0,
                "do": 0.8,
                "capable": 0.8,
                "ability": 0.8
            },
            category="query"
        )
        
        # Property query prefab
        self.core.add_prefab(
            "property_query",
            {
                "what": 0.8,
                "properties": 1.0,
                "attributes": 1.0,
                "characteristics": 1.0,
                "like": 0.6
            },
            category="query"
        )
        
        # Part query prefab
        self.core.add_prefab(
            "part_query",
            {
                "what": 0.8,
                "parts": 1.0,
                "components": 1.0,
                "contains": 0.8,
                "made": 0.7,
                "of": 0.7,
                "have": 0.8,
                "has": 0.8
            },
            category="query"
        )
        
        # Verification query prefab
        self.core.add_prefab(
            "verification_query",
            {
                "is": 1.0,
                "are": 1.0,
                "can": 0.8,
                "does": 0.8,
                "do": 0.8,
                "true": 0.7,
                "correct": 0.7
            },
            category="query"
        )
        
        # Used for query prefab
        self.core.add_prefab(
            "used_for_query",
            {
                "what": 0.8,
                "used": 1.0,
                "for": 1.0,
                "purpose": 0.9,
                "function": 0.9,
                "application": 0.8
            },
            category="query"
        )
        
        # Store query prefabs for reference
        self.query_prefabs = {
            "definition_query": {
                "query_type": "definition",
                "signal_purpose": "QUERY",
                "signal_payload": {"ask": "relation.is_a"}
            },
            "capability_query": {
                "query_type": "capability",
                "signal_purpose": "QUERY",
                "signal_payload": {"ask_relation": "can_do"}
            },
            "property_query": {
                "query_type": "property",
                "signal_purpose": "QUERY",
                "signal_payload": {"ask_relation": "has_property"}
            },
            "part_query": {
                "query_type": "part",
                "signal_purpose": "QUERY",
                "signal_payload": {"ask_relation": "has_part"}
            },
            "verification_query": {
                "query_type": "verification",
                "signal_purpose": "VERIFY",
                "signal_payload": {"relation": "is_a", "target": ""}
            },
            "used_for_query": {
                "query_type": "used_for",
                "signal_purpose": "QUERY",
                "signal_payload": {"ask_relation": "used_for"}
            }
        }
    
    def extract_entity(self, text: str) -> Optional[str]:
        """
        Extract the main entity from a query.
        
        Args:
            text: The query text
            
        Returns:
            The extracted entity or None
        """
        # Pre-process text to handle multi-word entities
        text = text.lower().strip()
        text = re.sub(r'artificial intelligence', 'artificial_intelligence', text)
        text = re.sub(r'machine learning', 'machine_learning', text)
        text = re.sub(r'deep learning', 'deep_learning', text)
        text = re.sub(r'neural network', 'neural_network', text)
        text = re.sub(r'police officer', 'police_officer', text)
        text = re.sub(r'human being', 'human_being', text)
        text = re.sub(r'living being', 'living_being', text)
        
        # Pattern for "what is X" or "what are X"
        what_is_match = re.search(r'what\s+(?:is|are)\s+(?:a|an|the)?\s*([a-z_]+)', text)
        if what_is_match:
            return what_is_match.group(1).strip()
        
        # Pattern for "can X do Y"
        can_do_match = re.search(r'(?:can|could|does)\s+([a-z_]+)\s+', text)
        if can_do_match:
            return can_do_match.group(1).strip()
        
        # Pattern for "does X have Y" or "do X have Y"
        does_have_match = re.search(r'(?:does|do|did)\s+([a-z_]+)\s+(?:have|has|contain)', text)
        if does_have_match:
            return does_have_match.group(1).strip()
        
        # Pattern for "is X a Y" or "are X a Y"
        is_a_match = re.search(r'(?:is|are|was|were)\s+([a-z_]+)\s+(?:a|an|the)', text)
        if is_a_match:
            return is_a_match.group(1).strip()
        
        # Pattern for "tell me about X"
        tell_about_match = re.search(r'(?:tell|explain|describe)(?:\s+\w+)?\s+(?:about|on)?\s+([a-z_]+)', text)
        if tell_about_match:
            return tell_about_match.group(1).strip()
        
        # Fallback: look for nouns that aren't common question words
        words = text.split()
        for word in words:
            if word not in {"what", "who", "where", "when", "why", "how",
                            "is", "are", "was", "were", "do", "does", "did",
                            "a", "an", "the", "in", "on", "at", "by", "for",
                            "tell", "me", "about", "explain", "describe"}:
                return word
        
        return None
    
    def extract_target(self, text: str) -> Optional[str]:
        """
        Extract the target entity from a verification query.
        
        Args:
            text: The query text
            
        Returns:
            The extracted target or None
        """
        # Pre-process text to handle multi-word entities
        text = text.lower().strip()
        text = re.sub(r'artificial intelligence', 'artificial_intelligence', text)
        text = re.sub(r'machine learning', 'machine_learning', text)
        text = re.sub(r'deep learning', 'deep_learning', text)
        text = re.sub(r'neural network', 'neural_network', text)
        text = re.sub(r'police officer', 'police_officer', text)
        text = re.sub(r'human being', 'human_being', text)
        text = re.sub(r'living being', 'living_being', text)
        
        # Pattern for "is X a Y" or "are X a Y"
        is_a_match = re.search(r'(?:is|are|was|were)\s+[a-z_]+\s+(?:a|an|the)\s+([a-z_]+)', text)
        if is_a_match:
            return is_a_match.group(1).strip()
        
        # Pattern for "can X do Y"
        can_do_match = re.search(r'(?:can|could|does)\s+[a-z_]+\s+([a-z_]+)', text)
        if can_do_match:
            return can_do_match.group(1).strip()
        
        # Pattern for "does X have Y" or "do X have Y"
        does_have_match = re.search(r'(?:does|do|did)\s+[a-z_]+\s+(?:have|has|contain)\s+(?:a|an|the)?\s*([a-z_]+)', text)
        if does_have_match:
            return does_have_match.group(1).strip()
        
        # Pattern for "is X made of Y"
        made_of_match = re.search(r'(?:is|are)\s+[a-z_]+\s+(?:made of|composed of|comprised of)\s+([a-z_]+)', text)
        if made_of_match:
            return made_of_match.group(1).strip()
            
        # Pattern for "what is X used for"
        used_for_match = re.search(r'what\s+(?:is|are)\s+[a-z_]+\s+(?:used for|utilized for|for)', text)
        if used_for_match:
            return "purpose"  # Return a placeholder for purpose
            
        # Pattern for "what is the purpose of X"
        purpose_match = re.search(r'what\s+(?:is|are)\s+the\s+(?:purpose|function|use|application)\s+of\s+[a-z_]+', text)
        if purpose_match:
            return "purpose"  # Return a placeholder for purpose
        
        return None
    
    def parse_query(self, text: str) -> Dict[str, Any]:
        """
        Parse a natural language query using the IRA approach.
        
        Args:
            text: The query text
            
        Returns:
            A structured representation of the query
        """
        # Process text through the IRA core
        result = self.core.process_text(text)
        
        # Extract entity and target
        entity = self.extract_entity(text)
        target = self.extract_target(text)
        
        # Determine query type based on activated prefabs
        query_type = "unknown"
        signal_purpose = "QUERY"
        signal_payload = {}
        
        for prefab_name in result["activated_prefabs"]:
            if prefab_name in self.query_prefabs:
                prefab_info = self.query_prefabs[prefab_name]
                query_type = prefab_info["query_type"]
                signal_purpose = prefab_info["signal_purpose"]
                signal_payload = prefab_info["signal_payload"].copy()
                break
        
        # Fill in entity and target
        if entity:
            if signal_purpose == "VERIFY" and target:
                signal_payload["target"] = target
        
        # Return structured query
        return {
            "entity": entity or "",
            "query_type": query_type,
            "attributes": {
                "target": target or ""
            },
            "signal_purpose": signal_purpose,
            "signal_payload": signal_payload,
            "activated_prefabs": result["activated_prefabs"],
            "prefab_activations": {k: v for k, v in result["prefab_activations"].items() if v > 0.2}
        }
    
    def extract_knowledge(self, text: str) -> List[Dict[str, str]]:
        """
        Extract knowledge triplets from text using the IRA approach.
        
        Args:
            text: The text to extract knowledge from
            
        Returns:
            A list of triplets (subject, relation, object)
        """
        triplets = []
        
        # Process text through the IRA core
        result = self.core.process_text(text)
        
        # Use regex patterns for basic triplet extraction
        text = text.lower().strip()
        
        # Pre-process text to handle multi-word entities
        # Replace common multi-word phrases with single tokens
        text = re.sub(r'artificial intelligence', 'artificial_intelligence', text)
        text = re.sub(r'machine learning', 'machine_learning', text)
        text = re.sub(r'deep learning', 'deep_learning', text)
        text = re.sub(r'neural network', 'neural_network', text)
        text = re.sub(r'police officer', 'police_officer', text)
        text = re.sub(r'human being', 'human_being', text)
        text = re.sub(r'living being', 'living_being', text)
        
        # Look for "X is a Y" patterns
        is_a_matches = re.finditer(r'([a-z_]+)\s+(?:is|are|was|were)\s+(?:a|an|the)?\s*([a-z_]+)(?:\s+and\s+(?:a|an|the)?\s*([a-z_]+))?', text)
        for match in is_a_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            
            # Skip if the object is just "a" or "an"
            if obj not in ["a", "an"]:
                triplets.append({"subject": subject, "relation": "is_a", "object": obj})
                
                # Create ideoms and connections
                subj_ideom = self.core.add_ideom(subject, "entity")
                obj_ideom = self.core.add_ideom(obj, "entity")
                subj_ideom.connect(obj, 0.8)
                
                # Check for second object (X is a Y and a Z)
                if match.group(3):
                    obj2 = match.group(3).strip()
                    if obj2 not in ["a", "an"]:
                        triplets.append({"subject": subject, "relation": "is_a", "object": obj2})
                        obj2_ideom = self.core.add_ideom(obj2, "entity")
                        subj_ideom.connect(obj2, 0.8)
        
        # Look for "X has Y" patterns
        has_matches = re.finditer(r'([a-z_]+)\s+(?:has|have|contains|with)\s+(?:a|an|the)?\s*([a-z_]+)(?:\s+and\s+(?:a|an|the)?\s*([a-z_]+))?', text)
        for match in has_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "has_part", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "entity")
            subj_ideom.connect(obj, 0.6)
            
            # Check for second object (X has Y and Z)
            if match.group(3):
                obj2 = match.group(3).strip()
                triplets.append({"subject": subject, "relation": "has_part", "object": obj2})
                obj2_ideom = self.core.add_ideom(obj2, "entity")
                subj_ideom.connect(obj2, 0.6)
        
        # Look for "X can Y" patterns
        can_matches = re.finditer(r'([a-z_]+)\s+(?:can|could|able to|capable of)\s+([a-z_]+)(?:\s+and\s+([a-z_]+))?', text)
        for match in can_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "can_do", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "action")
            subj_ideom.connect(obj, 0.7)
            
            # Check for second action (X can Y and Z)
            if match.group(3):
                obj2 = match.group(3).strip()
                triplets.append({"subject": subject, "relation": "can_do", "object": obj2})
                obj2_ideom = self.core.add_ideom(obj2, "action")
                subj_ideom.connect(obj2, 0.7)
        
        # Look for "X is Y" patterns (for properties)
        is_prop_matches = re.finditer(r'([a-z_]+)\s+(?:is|are|seems|appears)\s+([a-z_]+)(?:\s+and\s+([a-z_]+))?(?:\s+but\s+(?:not|also)\s+([a-z_]+))?', text)
        for match in is_prop_matches:
            subject = match.group(1).strip()
            prop1 = match.group(2).strip()
            
            # Skip if this is an "is a" pattern we already captured
            if prop1 in {"a", "an"}:
                continue
                
            triplets.append({"subject": subject, "relation": "has_property", "object": prop1})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            prop_ideom = self.core.add_ideom(prop1, "property")
            subj_ideom.connect(prop1, 0.5)
            
            # Check for second property (X is Y and Z)
            if match.group(3):
                prop2 = match.group(3).strip()
                triplets.append({"subject": subject, "relation": "has_property", "object": prop2})
                
                # Create ideom and connection
                prop2_ideom = self.core.add_ideom(prop2, "property")
                subj_ideom.connect(prop2, 0.5)
            
            # Check for contrasting property (X is Y but not Z)
            if match.group(4):
                prop3 = match.group(4).strip()
                # For "but not", create a negative property
                if "not" in text:
                    triplets.append({"subject": subject, "relation": "not_property", "object": prop3})
                else:
                    triplets.append({"subject": subject, "relation": "has_property", "object": prop3})
                    prop3_ideom = self.core.add_ideom(prop3, "property")
                    subj_ideom.connect(prop3, 0.5)
        
        # Look for "X consists of Y" patterns
        consists_matches = re.finditer(r'([a-z_]+)\s+(?:consists of|comprises|includes|made up of|made of)\s+(?:a|an|the)?\s*([a-z_]+)(?:\s+and\s+(?:a|an|the)?\s*([a-z_]+))?', text)
        for match in consists_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "has_part", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "entity")
            subj_ideom.connect(obj, 0.7)  # Stronger connection for "consists of"
            
            # Check for second part (X consists of Y and Z)
            if match.group(3):
                obj2 = match.group(3).strip()
                triplets.append({"subject": subject, "relation": "has_part", "object": obj2})
                obj2_ideom = self.core.add_ideom(obj2, "entity")
                subj_ideom.connect(obj2, 0.7)
        
        # Look for "X used for Y" patterns
        used_for_matches = re.finditer(r'([a-z_]+)\s+(?:used for|utilized for|employed for|for|used to)\s+([a-z_]+)(?:\s+and\s+([a-z_]+))?', text)
        for match in used_for_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "used_for", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "purpose")
            subj_ideom.connect(obj, 0.6)
            
            # Check for second purpose (X used for Y and Z)
            if match.group(3):
                obj2 = match.group(3).strip()
                triplets.append({"subject": subject, "relation": "used_for", "object": obj2})
                obj2_ideom = self.core.add_ideom(obj2, "purpose")
                subj_ideom.connect(obj2, 0.6)
        
        # Add additional patterns for complex relationships
        
        # "X drives Y" pattern (for human drives car, etc.)
        drives_matches = re.finditer(r'([a-z_]+)\s+(?:drives|operates|controls)\s+(?:a|an|the)?\s*([a-z_]+)', text)
        for match in drives_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "drives", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "entity")
            subj_ideom.connect(obj, 0.6)
        
        # "X is alive" pattern
        alive_matches = re.finditer(r'([a-z_]+)\s+(?:is|are)\s+(?:alive|living)', text)
        for match in alive_matches:
            subject = match.group(1).strip()
            triplets.append({"subject": subject, "relation": "has_property", "object": "alive"})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            alive_ideom = self.core.add_ideom("alive", "property")
            subj_ideom.connect("alive", 0.7)
        
        # "X is a type of Y" pattern
        type_of_matches = re.finditer(r'([a-z_]+)\s+(?:is|are)\s+(?:a|an)?\s*type\s+of\s+([a-z_]+)', text)
        for match in type_of_matches:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            triplets.append({"subject": subject, "relation": "is_a", "object": obj})
            
            # Create ideoms and connections
            subj_ideom = self.core.add_ideom(subject, "entity")
            obj_ideom = self.core.add_ideom(obj, "entity")
            subj_ideom.connect(obj, 0.8)  # Strong connection for "type of"
        
        # Save the updated model
        self.core.save()
        
        return triplets


class IRALanguageGeneration:
    """
    Language generation module based on the IRA philosophy.
    
    This class uses the IRA language core to generate natural language
    by activating prefabs and constructing responses based on activated patterns.
    """
    
    def __init__(self, core: Optional[IRALanguageCore] = None):
        """
        Initialize the language generation module.
        
        Args:
            core: The IRA language core (created if None)
        """
        self.core = core or IRALanguageCore()
        self.response_templates: Dict[str, List[str]] = {}
        self.response_prefabs: Dict[str, Dict[str, Any]] = {}
        
        # Initialize response templates and prefabs if needed
        if not self.core.prefabs:
            self._initialize_response_components()
    
    def _initialize_response_components(self):
        """Initialize templates and prefabs for responses."""
        # Define response templates
        self.response_templates = {
            "definition": [
                "{entity} is {definition}.",
                "A {entity} is defined as {definition}.",
                "{entity} refers to {definition}.",
                "The term {entity} means {definition}.",
                "{entity} can be described as {definition}."
            ],
            "capability": [
                "{entity} can {capabilities}.",
                "A {entity} is capable of {capabilities}.",
                "{entity} has the ability to {capabilities}.",
                "{entity} is designed to {capabilities}.",
                "The primary function of {entity} is to {capabilities}."
            ],
            "part": [
                "{entity} has {parts}.",
                "A {entity} consists of {parts}.",
                "{entity} contains {parts}.",
                "The components of {entity} include {parts}.",
                "{entity} is made up of {parts}."
            ],
            "property": [
                "{entity} is {properties}.",
                "A {entity} is characterized by being {properties}.",
                "{entity} has the following properties: {properties}.",
                "The attributes of {entity} include being {properties}.",
                "{entity} is typically {properties}."
            ],
            "verification_positive": [
                "Yes, {entity} {relation} {target}.",
                "That's correct, {entity} {relation} {target}.",
                "Indeed, {entity} {relation} {target}.",
                "You're right, {entity} {relation} {target}.",
                "Affirmative, {entity} {relation} {target}."
            ],
            "verification_negative": [
                "No, {entity} does not {relation} {target}.",
                "I don't believe {entity} {relation} {target}.",
                "As far as I know, {entity} does not {relation} {target}.",
                "That's incorrect, {entity} doesn't {relation} {target}.",
                "I cannot confirm that {entity} {relation} {target}."
            ],
            "unknown_concept": [
                "I don't have information about {entity} in my knowledge base.",
                "I'm not familiar with {entity}.",
                "I don't know about {entity}.",
                "I don't have data on {entity} in my system.",
                "{entity} is not something I have information about."
            ],
            "error": [
                "I'm sorry, I couldn't understand that question. Could you rephrase it?",
                "I'm having trouble understanding your question. Could you ask it differently?",
                "I didn't quite catch that. Can you rephrase your question?",
                "I'm not sure I understand what you're asking. Could you clarify?",
                "Your question is unclear to me. Could you try asking in a different way?"
            ],
            "used_for": [
                "{entity} is used for {purpose}.",
                "A {entity} is typically used to {purpose}.",
                "The primary purpose of {entity} is for {purpose}.",
                "{entity} is designed for {purpose}.",
                "People use {entity} to {purpose}."
            ]
        }
        
        # Create response prefabs
        self.core.add_prefab(
            "definition_response",
            {
                "entity": 1.0,
                "is": 0.8,
                "definition": 1.0,
                "describe": 0.6
            },
            category="response"
        )
        
        self.core.add_prefab(
            "capability_response",
            {
                "entity": 1.0,
                "can": 0.8,
                "ability": 0.7,
                "capable": 0.7
            },
            category="response"
        )
        
        self.core.add_prefab(
            "part_response",
            {
                "entity": 1.0,
                "has": 0.8,
                "contains": 0.7,
                "consists": 0.7,
                "parts": 0.9
            },
            category="response"
        )
        
        self.core.add_prefab(
            "property_response",
            {
                "entity": 1.0,
                "is": 0.8,
                "properties": 0.9,
                "characteristics": 0.7
            },
            category="response"
        )
        
        self.core.add_prefab(
            "verification_response",
            {
                "entity": 1.0,
                "yes": 0.8,
                "no": 0.8,
                "correct": 0.7,
                "indeed": 0.6
            },
            category="response"
        )
        
        # Add used_for response prefab
        self.core.add_prefab(
            "used_for_response",
            {
                "entity": 1.0,
                "used": 0.8,
                "for": 0.8,
                "purpose": 0.7,
                "function": 0.7
            },
            category="response"
        )
        
        # Store response prefabs for reference
        self.response_prefabs = {
            "definition_response": {
                "template_key": "definition"
            },
            "capability_response": {
                "template_key": "capability"
            },
            "part_response": {
                "template_key": "part"
            },
            "property_response": {
                "template_key": "property"
            },
            "verification_response": {
                "template_key": "verification_positive"
            },
            "used_for_response": {
                "template_key": "used_for"
            }
        }
    
    def select_template(self, response_type: str, data: Dict[str, Any]) -> str:
        """
        Select an appropriate template for the response.
        
        Args:
            response_type: The type of response
            data: Data for the response
            
        Returns:
            The selected template
        """
        # Handle verification responses
        if response_type == "verification":
            verified = data.get("verified", False)
            key = "verification_positive" if verified else "verification_negative"
            templates = self.response_templates.get(key, [])
        else:
            # Get templates for the response type
            templates = self.response_templates.get(response_type, [])
        
        # If no templates are found, use error templates
        if not templates:
            templates = self.response_templates.get("error", ["I'm not sure how to respond to that."])
        
        # If templates is still empty, use a default template
        if not templates:
            return "I'm not sure how to respond to that."
            
        # Select a random template
        return random.choice(templates)
    
    def generate_response(self, data: Dict[str, Any]) -> str:
        """
        Generate a natural language response using the IRA approach.
        
        Args:
            data: Data for the response
            
        Returns:
            The generated response
        """
        # Determine response type
        response_type = data.get("response_type", "unknown")
        
        # Activate ideoms based on the data
        self.core.reset_activations()
        
        # Activate entity ideom
        entity = data.get("entity", "")
        if entity:
            if entity in self.core.ideoms:
                self.core.ideoms[entity].activate(1.0)
        
        # Activate other relevant ideoms based on response type
        if response_type == "definition":
            for ideom_name in ["is", "definition", "describe"]:
                if ideom_name in self.core.ideoms:
                    self.core.ideoms[ideom_name].activate(0.8)
        elif response_type == "capability":
            for ideom_name in ["can", "ability", "capable"]:
                if ideom_name in self.core.ideoms:
                    self.core.ideoms[ideom_name].activate(0.8)
        elif response_type == "part":
            for ideom_name in ["has", "contains", "parts"]:
                if ideom_name in self.core.ideoms:
                    self.core.ideoms[ideom_name].activate(0.8)
        elif response_type == "used_for":
            for ideom_name in ["used", "for", "purpose", "function"]:
                if ideom_name in self.core.ideoms:
                    self.core.ideoms[ideom_name].activate(0.8)
        elif response_type == "verification":
            verified = data.get("verified", False)
            if verified:
                for ideom_name in ["yes", "correct", "indeed"]:
                    if ideom_name in self.core.ideoms:
                        self.core.ideoms[ideom_name].activate(0.8)
            else:
                for ideom_name in ["no", "not", "don't"]:
                    if ideom_name in self.core.ideoms:
                        self.core.ideoms[ideom_name].activate(0.8)
        
        # Propagate activation
        prefab_activations = self.core.propagate_activation()
        
        # Get activated prefabs
        activated_prefabs = self.core.get_activated_prefabs()
        
        # Select template based on activated prefabs
        template_key = response_type
        for prefab_name in activated_prefabs:
            if prefab_name in self.response_prefabs:
                template_key = self.response_prefabs[prefab_name]["template_key"]
                break
        
        # Select a template
        template = self.select_template(template_key, data)
        
        # Fill in the template
        try:
            # Handle different response types
            if response_type == "definition":
                definition = data.get("definition", "")
                return template.format(entity=entity, definition=definition)
            elif response_type == "capability":
                capabilities = data.get("capabilities", [])
                capabilities_text = ", ".join(capabilities) if capabilities else "do various things"
                return template.format(entity=entity, capabilities=capabilities_text)
            elif response_type == "part":
                parts = data.get("parts", [])
                parts_text = ", ".join(parts) if parts else "various components"
                return template.format(entity=entity, parts=parts_text)
            elif response_type == "property":
                properties = data.get("properties", [])
                properties_text = ", ".join(properties) if properties else "various properties"
                return template.format(entity=entity, properties=properties_text)
            elif response_type == "used_for":
                purpose = data.get("purpose", "")
                return template.format(entity=entity, purpose=purpose)
            elif response_type == "verification":
                target = data.get("target", "")
                relation = data.get("relation", "is_a")
                
                # Convert relation to readable form
                relation_text = relation
                if relation == "is_a":
                    relation_text = "is a"
                elif relation == "can_do":
                    relation_text = "can"
                elif relation == "has_part":
                    relation_text = "has"
                elif relation == "used_for":
                    relation_text = "is used for"
                    
                return template.format(entity=entity, relation=relation_text, target=target)
            elif response_type == "unknown_concept":
                return template.format(entity=entity)
            else:
                return template
        except KeyError as e:
            logger.warning(f"Missing data for template: {e}")
            return "I'm not sure how to respond to that."


class IRALanguageModule:
    """
    Complete IRA language module that integrates understanding and generation.
    
    This class provides a unified interface for language understanding and
    generation based on the IRA philosophy.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the IRA language module.
        
        Args:
            model_path: Path to the model files (if None, uses default paths)
        """
        self.model_path = model_path or Path("models/ira_language")
        self.core = IRALanguageCore(self.model_path)
        self.understanding = IRALanguageUnderstanding(self.core)
        self.generation = IRALanguageGeneration(self.core)
    
    def parse_query(self, text: str) -> Dict[str, Any]:
        """
        Parse a natural language query.
        
        Args:
            text: The query text
            
        Returns:
            A structured representation of the query
        """
        return self.understanding.parse_query(text)
    
    def generate_response(self, data: Dict[str, Any]) -> str:
        """
        Generate a natural language response.
        
        Args:
            data: Data for the response
            
        Returns:
            The generated response
        """
        return self.generation.generate_response(data)
    
    def extract_knowledge(self, text: str) -> List[Dict[str, str]]:
        """
        Extract knowledge triplets from text.
        
        Args:
            text: The text to extract knowledge from
            
        Returns:
            A list of triplets (subject, relation, object)
        """
        return self.understanding.extract_knowledge(text)
    
    def train(self, texts: List[str], save: bool = True):
        """
        Train the model on a list of texts.
        
        Args:
            texts: List of training texts
            save: Whether to save the model after training
        """
        logger.info(f"Training IRA language module on {len(texts)} texts")
        
        # Extract knowledge from each text
        for text in texts:
            self.extract_knowledge(text)
        
        # Save the model if requested
        if save:
            self.core.save()