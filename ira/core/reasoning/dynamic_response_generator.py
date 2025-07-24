"""
DynamicResponseGenerator module for the Unified Reasoning Core.

This module defines the DynamicResponseGenerator class, which is responsible for
generating responses without templates in the IRA (Ideom Resolver AI) architecture.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import random
from .ideom_network import IdeomNetwork
from .activation_pattern import ActivationPattern
from .prefab import Prefab


class DynamicResponseGenerator:
    """
    A generator for dynamic responses without templates.
    
    The DynamicResponseGenerator is responsible for generating responses without
    relying on templates, using the activation pattern and ideom network to
    construct responses dynamically.
    
    Attributes:
        ideom_network: The ideom network to use for response generation.
        max_response_length: The maximum length of generated responses.
        min_response_length: The minimum length of generated responses.
        coherence_threshold: The threshold for ensuring response coherence.
    """
    
    def __init__(
        self,
        ideom_network: IdeomNetwork,
        max_response_length: int = 50,
        min_response_length: int = 5,
        coherence_threshold: float = 0.3
    ):
        """
        Initialize a dynamic response generator.
        
        Args:
            ideom_network: The ideom network to use for response generation.
            max_response_length: The maximum length of generated responses.
            min_response_length: The minimum length of generated responses.
            coherence_threshold: The threshold for ensuring response coherence.
        """
        self.ideom_network = ideom_network
        self.max_response_length = max_response_length
        self.min_response_length = min_response_length
        self.coherence_threshold = coherence_threshold
    
    def generate_response(
        self,
        activation_pattern: ActivationPattern,
        seed_words: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response based on the activation pattern.
        
        This method generates a response by starting with seed words (if provided)
        or the most active ideoms, and then expanding the response by adding
        connected ideoms based on their activation levels and connection strengths.
        
        Args:
            activation_pattern: The activation pattern to generate a response from.
            seed_words: Optional seed words to start the response with.
            
        Returns:
            The generated response.
        """
        # Get the most active ideoms
        most_active_ideoms = activation_pattern.get_most_active_ideoms(10)
        
        # Get ideom names
        ideom_names = {}
        for ideom_id in most_active_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                ideom_names[ideom_id] = ideom.name
        
        # Start with seed words or most active ideoms
        if seed_words and len(seed_words) > 0:
            response_words = seed_words.copy()
        else:
            # Use the names of the most active ideoms as seed words
            response_words = []
            for ideom_id in most_active_ideoms[:3]:  # Use top 3 ideoms
                if ideom_id in ideom_names:
                    response_words.append(ideom_names[ideom_id])
        
        # Expand the response
        return self._expand_response(response_words, activation_pattern, ideom_names)
    
    def _expand_response(
        self,
        seed_words: List[str],
        activation_pattern: ActivationPattern,
        ideom_names: Dict[str, str]
    ) -> str:
        """
        Expand a response from seed words.
        
        Args:
            seed_words: The seed words to start with.
            activation_pattern: The activation pattern to use for expansion.
            ideom_names: A dictionary mapping ideom IDs to their names.
            
        Returns:
            The expanded response.
        """
        # Start with seed words
        response_words = seed_words.copy()
        
        # Get all active ideoms
        active_ideoms = activation_pattern.get_active_ideoms()
        
        # Keep track of used ideoms to avoid repetition
        used_ideoms = set()
        for word in seed_words:
            # Find ideoms with this name
            for ideom_id, name in ideom_names.items():
                if name.lower() == word.lower():
                    used_ideoms.add(ideom_id)
        
        # Expand the response until we reach the maximum length
        while len(response_words) < self.max_response_length:
            # Get the last word in the response
            if not response_words:
                break
                
            last_word = response_words[-1]
            
            # Find ideoms with this name
            last_ideom_ids = []
            for ideom_id, name in ideom_names.items():
                if name.lower() == last_word.lower():
                    last_ideom_ids.append(ideom_id)
            
            # If no matching ideoms, try to find semantically similar ones
            if not last_ideom_ids:
                last_ideom_ids = self._find_similar_ideoms(last_word)
            
            # If still no matching ideoms, add a random active ideom
            if not last_ideom_ids and active_ideoms:
                unused_active_ideoms = [ideom_id for ideom_id in active_ideoms if ideom_id not in used_ideoms]
                if unused_active_ideoms:
                    last_ideom_ids = [random.choice(unused_active_ideoms)]
                else:
                    # If all active ideoms are used, break
                    break
            
            # If no ideoms to expand from, break
            if not last_ideom_ids:
                break
            
            # Get connected ideoms for each last ideom
            next_ideom_candidates = []
            for last_ideom_id in last_ideom_ids:
                last_ideom = self.ideom_network.get_ideom(last_ideom_id)
                if last_ideom:
                    # Get connected ideoms with their connection strengths
                    for connected_id, strength in last_ideom.connections.items():
                        if strength >= self.coherence_threshold and connected_id not in used_ideoms:
                            # Check if the connected ideom is active
                            activation = activation_pattern.get_activation_level(connected_id)
                            if activation > 0:
                                # Calculate a score based on connection strength and activation
                                score = strength * activation
                                next_ideom_candidates.append((connected_id, score))
            
            # If no candidates, break
            if not next_ideom_candidates:
                break
            
            # Sort candidates by score
            next_ideom_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Select the top candidate
            next_ideom_id = next_ideom_candidates[0][0]
            next_ideom = self.ideom_network.get_ideom(next_ideom_id)
            
            if next_ideom:
                # Add the ideom name to the response
                response_words.append(next_ideom.name)
                used_ideoms.add(next_ideom_id)
            else:
                # If the ideom doesn't exist, break
                break
        
        # Ensure minimum length
        if len(response_words) < self.min_response_length and active_ideoms:
            # Add more words from active ideoms
            unused_active_ideoms = [ideom_id for ideom_id in active_ideoms if ideom_id not in used_ideoms]
            while len(response_words) < self.min_response_length and unused_active_ideoms:
                # Select a random unused active ideom
                next_ideom_id = random.choice(unused_active_ideoms)
                unused_active_ideoms.remove(next_ideom_id)
                
                next_ideom = self.ideom_network.get_ideom(next_ideom_id)
                if next_ideom:
                    # Add the ideom name to the response
                    response_words.append(next_ideom.name)
                    used_ideoms.add(next_ideom_id)
        
        # Convert to a sentence
        return self._format_response(response_words)
    
    def _format_response(self, words: List[str]) -> str:
        """
        Format a list of words into a coherent response.
        
        Args:
            words: The words to format.
            
        Returns:
            The formatted response.
        """
        # Simple formatting: join words with spaces and capitalize the first letter
        if not words:
            return ""
        
        # Add appropriate articles and conjunctions
        formatted_words = []
        for i, word in enumerate(words):
            if i == 0:
                # Capitalize the first word
                formatted_words.append(word.capitalize())
            elif i == len(words) - 1 and len(words) > 1:
                # Add "and" before the last word if there are multiple words
                formatted_words.append("and " + word)
            else:
                # Add the word as is
                formatted_words.append(word)
        
        # Join words with spaces
        response = " ".join(formatted_words)
        
        # Add a period at the end if there isn't one
        if not response.endswith(".") and not response.endswith("?") and not response.endswith("!"):
            response += "."
        
        return response
    
    def _find_similar_ideoms(self, word: str) -> List[str]:
        """
        Find ideoms with names similar to the given word.
        
        Args:
            word: The word to find similar ideoms for.
            
        Returns:
            A list of ideom IDs with similar names.
        """
        similar_ideoms = []
        
        # Get all ideoms
        all_ideoms = self.ideom_network.get_all_ideoms()
        
        for ideom in all_ideoms:
            # Calculate similarity between word and ideom name
            similarity = self._calculate_similarity(word, ideom.name)
            
            if similarity >= 0.7:  # Threshold for similarity
                similar_ideoms.append(ideom.id)
        
        return similar_ideoms
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate the similarity between two words.
        
        Args:
            word1: The first word.
            word2: The second word.
            
        Returns:
            The similarity score (0.0 to 1.0).
        """
        # Simple character-based similarity
        if word1 == word2:
            return 1.0
        
        # Normalize words
        word1 = word1.lower()
        word2 = word2.lower()
        
        # Check for prefix match
        min_length = min(len(word1), len(word2))
        for i in range(min_length):
            if word1[i] != word2[i]:
                prefix_length = i
                break
        else:
            prefix_length = min_length
        
        # Calculate similarity based on prefix length
        similarity = prefix_length / max(len(word1), len(word2))
        
        return similarity
    
    def generate_responses(
        self,
        activation_pattern: ActivationPattern,
        count: int = 3
    ) -> List[str]:
        """
        Generate multiple responses based on the activation pattern.
        
        Args:
            activation_pattern: The activation pattern to generate responses from.
            count: The number of responses to generate.
            
        Returns:
            A list of generated responses.
        """
        responses = []
        
        # Get the most active ideoms
        most_active_ideoms = activation_pattern.get_most_active_ideoms(10)
        
        # Get ideom names
        ideom_names = {}
        for ideom_id in most_active_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                ideom_names[ideom_id] = ideom.name
        
        # Generate multiple responses with different seed words
        for i in range(count):
            # Use different seed words for each response
            if i == 0:
                # First response: use the most active ideoms
                seed_words = [ideom_names[ideom_id] for ideom_id in most_active_ideoms[:2] if ideom_id in ideom_names]
            elif i == 1:
                # Second response: use a random selection of active ideoms
                active_ideoms = list(activation_pattern.get_active_ideoms())
                if active_ideoms:
                    random_ideoms = random.sample(active_ideoms, min(2, len(active_ideoms)))
                    seed_words = [ideom_names[ideom_id] for ideom_id in random_ideoms if ideom_id in ideom_names]
                else:
                    seed_words = []
            else:
                # Other responses: use a combination of previous seed words
                seed_words = []
                if responses:
                    # Extract words from previous responses
                    prev_words = []
                    for response in responses:
                        prev_words.extend(response.lower().split())
                    
                    # Select random words from previous responses
                    if prev_words:
                        seed_words = random.sample(prev_words, min(2, len(prev_words)))
            
            # Generate a response with these seed words
            response = self.generate_response(activation_pattern, seed_words)
            
            # Add to the list if it's not empty and not a duplicate
            if response and response not in responses:
                responses.append(response)
        
        return responses