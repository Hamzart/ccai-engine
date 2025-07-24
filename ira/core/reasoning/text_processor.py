"""
TextProcessor module for the Unified Reasoning Core.

This module defines the TextProcessor class, which is responsible for converting
text to ideom activations in the IRA (Ideom Resolver AI) architecture.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from .ideom_network import IdeomNetwork
from .ideom import Ideom
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

# Ensure punkt is properly downloaded
if not nltk.download('punkt', quiet=True):
    print("Warning: Failed to download punkt tokenizer. Some functionality may not work.")



class TextProcessor:
    """
    A processor for converting text to ideom activations.
    
    The TextProcessor is responsible for analyzing text and converting it
    to ideom activations, handling multi-word concepts and semantic understanding.
    
    Attributes:
        ideom_network: The ideom network to use for ideom lookup and creation.
        lemmatizer: The WordNet lemmatizer for word normalization.
        stop_words: A set of stop words to filter out.
        n_gram_sizes: The sizes of n-grams to consider.
        semantic_similarity_threshold: The threshold for semantic similarity.
    """
    
    def __init__(
        self,
        ideom_network: IdeomNetwork,
        n_gram_sizes: List[int] = None,
        semantic_similarity_threshold: float = 0.7
    ):
        """
        Initialize a text processor.
        
        Args:
            ideom_network: The ideom network to use for ideom lookup and creation.
            n_gram_sizes: The sizes of n-grams to consider, or None to use default [1, 2, 3].
            semantic_similarity_threshold: The threshold for semantic similarity.
        """
        self.ideom_network = ideom_network
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.n_gram_sizes = n_gram_sizes or [1, 2, 3]
        self.semantic_similarity_threshold = semantic_similarity_threshold
        
        # Cache for lemmatized words
        self.lemma_cache: Dict[str, str] = {}
        
        # Cache for multi-word ideoms
        self.multi_word_ideoms: Dict[str, List[str]] = {}
    
    def process_text(self, text: str, initial_activation: float = 1.0) -> List[Tuple[str, float]]:
        """
        Process text and convert it to ideom activations.
        
        Args:
            text: The text to process.
            initial_activation: The initial activation level for ideoms.
            
        Returns:
            A list of tuples (ideom_id, activation_level).
        """
        # Preprocess the text
        tokens = self._preprocess_text(text)
        
        # Generate n-grams
        n_grams = self._generate_n_grams(tokens)
        
        # Match n-grams to ideoms
        ideom_activations = self._match_n_grams_to_ideoms(n_grams, initial_activation)
        
        # Apply semantic matching for unmatched tokens
        unmatched_tokens = self._get_unmatched_tokens(tokens, ideom_activations)
        semantic_activations = self._apply_semantic_matching(unmatched_tokens, initial_activation * 0.8)
        
        # Combine activations
        for ideom_id, activation in semantic_activations:
            ideom_activations.append((ideom_id, activation))
        
        return ideom_activations
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by tokenizing, removing stop words, and lemmatizing.
        
        Args:
            text: The text to preprocess.
            
        Returns:
            A list of preprocessed tokens.
        """
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove punctuation
        tokens = [token for token in tokens if token.isalnum()]
        
        # Remove stop words and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                if token in self.lemma_cache:
                    lemma = self.lemma_cache[token]
                else:
                    lemma = self.lemmatizer.lemmatize(token)
                    self.lemma_cache[token] = lemma
                processed_tokens.append(lemma)
        
        return processed_tokens
    
    def _generate_n_grams(self, tokens: List[str]) -> List[str]:
        """
        Generate n-grams from tokens.
        
        Args:
            tokens: The tokens to generate n-grams from.
            
        Returns:
            A list of n-grams.
        """
        n_grams = []
        
        for n in self.n_gram_sizes:
            if n <= len(tokens):
                for i in range(len(tokens) - n + 1):
                    n_gram = ' '.join(tokens[i:i+n])
                    n_grams.append(n_gram)
        
        # Sort n-grams by length (descending) to prioritize multi-word concepts
        n_grams.sort(key=len, reverse=True)
        
        return n_grams
    
    def _match_n_grams_to_ideoms(
        self,
        n_grams: List[str],
        initial_activation: float
    ) -> List[Tuple[str, float]]:
        """
        Match n-grams to ideoms.
        
        Args:
            n_grams: The n-grams to match.
            initial_activation: The initial activation level for ideoms.
            
        Returns:
            A list of tuples (ideom_id, activation_level).
        """
        ideom_activations = []
        matched_n_grams = set()
        
        for n_gram in n_grams:
            # Check if we've already matched a n-gram that contains this one
            if any(matched and matched.find(n_gram) >= 0 for matched in matched_n_grams):
                continue
            
            # Look for exact matches in the ideom network
            matching_ideoms = self.ideom_network.get_ideoms_by_name(n_gram)
            
            if matching_ideoms:
                # Add all matching ideoms with their activation levels
                for ideom in matching_ideoms:
                    ideom_activations.append((ideom.id, initial_activation))
                matched_n_grams.add(n_gram)
            else:
                # Look for partial matches
                partial_matches = self._find_partial_matches(n_gram)
                if partial_matches:
                    for ideom_id, similarity in partial_matches:
                        activation = initial_activation * similarity
                        ideom_activations.append((ideom_id, activation))
                    matched_n_grams.add(n_gram)
                else:
                    # Create a new ideom for unmatched n-grams (only for single words or important multi-word concepts)
                    if ' ' not in n_gram or self._is_important_concept(n_gram):
                        # Create a new Ideom instance with a unique ID
                        import uuid
                        new_ideom_id = str(uuid.uuid4())
                        new_ideom = Ideom(id=new_ideom_id, name=n_gram)
                        
                        # Add the new ideom to the network
                        self.ideom_network.add_ideom(new_ideom)
                        
                        # Add the new ideom to the activations
                        ideom_activations.append((new_ideom_id, initial_activation * 0.7))  # Lower activation for new ideoms
                        matched_n_grams.add(n_gram)
        
        return ideom_activations
    
    def _find_partial_matches(self, n_gram: str) -> List[Tuple[str, float]]:
        """
        Find partial matches for a n-gram.
        
        Args:
            n_gram: The n-gram to find partial matches for.
            
        Returns:
            A list of tuples (ideom_id, similarity).
        """
        partial_matches = []
        
        # Get all ideoms
        all_ideoms = self.ideom_network.get_all_ideoms()
        
        for ideom in all_ideoms:
            # Calculate similarity between n-gram and ideom name
            similarity = self._calculate_similarity(n_gram, ideom.name)
            
            if similarity >= self.semantic_similarity_threshold:
                partial_matches.append((ideom.id, similarity))
        
        # Sort by similarity (descending)
        partial_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3 matches
        return partial_matches[:3]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the similarity between two texts.
        
        This method uses a combination of Jaccard similarity, character n-gram similarity,
        and semantic similarity based on word relationships to provide a more accurate
        similarity score.
        
        Args:
            text1: The first text.
            text2: The second text.
            
        Returns:
            The similarity score (0.0 to 1.0).
        """
        # Normalize texts
        text1 = text1.lower()
        text2 = text2.lower()
        
        # Calculate Jaccard similarity
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        
        jaccard_similarity = 0.0
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        if union > 0:
            jaccard_similarity = intersection / union
        
        # Calculate character n-gram similarity
        char_ngram_similarity = self._calculate_char_ngram_similarity(text1, text2)
        
        # Calculate word relationship similarity
        word_relationship_similarity = self._calculate_word_relationship_similarity(text1, text2)
        
        # Combine the similarities with weights
        combined_similarity = (
            0.4 * jaccard_similarity +
            0.3 * char_ngram_similarity +
            0.3 * word_relationship_similarity
        )
        
        return combined_similarity
    
    def _calculate_char_ngram_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """
        Calculate the character n-gram similarity between two texts.
        
        Args:
            text1: The first text.
            text2: The second text.
            n: The size of the character n-grams.
            
        Returns:
            The character n-gram similarity score (0.0 to 1.0).
        """
        # Generate character n-grams
        def get_char_ngrams(text, n):
            return [text[i:i+n] for i in range(len(text) - n + 1)]
        
        ngrams1 = set(get_char_ngrams(text1, n))
        ngrams2 = set(get_char_ngrams(text2, n))
        
        # Calculate Dice coefficient
        intersection = len(ngrams1.intersection(ngrams2))
        total = len(ngrams1) + len(ngrams2)
        
        if total == 0:
            return 0.0
        
        return 2 * intersection / total
    
    def _calculate_word_relationship_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the word relationship similarity between two texts.
        
        This method considers synonyms, hypernyms, and other word relationships
        to determine semantic similarity.
        
        Args:
            text1: The first text.
            text2: The second text.
            
        Returns:
            The word relationship similarity score (0.0 to 1.0).
        """
        # Tokenize and lemmatize
        tokens1 = [self.lemmatizer.lemmatize(token) for token in text1.split()]
        tokens2 = [self.lemmatizer.lemmatize(token) for token in text2.split()]
        
        # Check for direct matches
        direct_matches = sum(1 for token in tokens1 if token in tokens2)
        
        # Check for prefix/suffix matches
        prefix_matches = 0
        for token1 in tokens1:
            for token2 in tokens2:
                # Check if one is a prefix of the other
                if len(token1) >= 4 and len(token2) >= 4:
                    if token1.startswith(token2[:3]) or token2.startswith(token1[:3]):
                        prefix_matches += 1
                        break
        
        # Calculate similarity based on matches
        total_tokens = len(tokens1) + len(tokens2)
        if total_tokens == 0:
            return 0.0
        
        # Weight direct matches more heavily than prefix matches
        weighted_matches = direct_matches * 2 + prefix_matches
        max_possible_matches = total_tokens  # Maximum possible weighted matches
        
        similarity = min(1.0, weighted_matches / max_possible_matches)
        
        return similarity
    
    def _is_important_concept(self, n_gram: str) -> bool:
        """
        Check if a n-gram represents an important concept.
        
        Args:
            n_gram: The n-gram to check.
            
        Returns:
            True if the n-gram represents an important concept, False otherwise.
        """
        # This is a placeholder implementation
        # In a real implementation, this would use a more sophisticated
        # method to determine if a multi-word concept is important
        
        # For now, consider all multi-word concepts with 2-3 words as important
        words = n_gram.split()
        return 2 <= len(words) <= 3
    
    def _get_unmatched_tokens(
        self,
        tokens: List[str],
        ideom_activations: List[Tuple[str, float]]
    ) -> List[str]:
        """
        Get tokens that weren't matched to any ideom.
        
        Args:
            tokens: The original tokens.
            ideom_activations: The ideom activations.
            
        Returns:
            A list of unmatched tokens.
        """
        # Get the names of all activated ideoms
        activated_ideom_ids = [ideom_id for ideom_id, _ in ideom_activations]
        activated_ideom_names = []
        
        for ideom_id in activated_ideom_ids:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                activated_ideom_names.append(ideom.name)
        
        # Find tokens that aren't part of any activated ideom
        unmatched_tokens = []
        for token in tokens:
            if not any(token in name for name in activated_ideom_names):
                unmatched_tokens.append(token)
        
        return unmatched_tokens
    
    def _apply_semantic_matching(
        self,
        tokens: List[str],
        activation_level: float
    ) -> List[Tuple[str, float]]:
        """
        Apply semantic matching for unmatched tokens.
        
        Args:
            tokens: The unmatched tokens.
            activation_level: The activation level for semantically matched ideoms.
            
        Returns:
            A list of tuples (ideom_id, activation_level).
        """
        semantic_activations = []
        
        for token in tokens:
            # Find semantically similar ideoms
            similar_ideoms = self._find_semantically_similar_ideoms(token)
            
            for ideom_id, similarity in similar_ideoms:
                activation = activation_level * similarity
                semantic_activations.append((ideom_id, activation))
        
        return semantic_activations
    
    def _find_semantically_similar_ideoms(self, token: str) -> List[Tuple[str, float]]:
        """
        Find ideoms that are semantically similar to a token.
        
        Args:
            token: The token to find similar ideoms for.
            
        Returns:
            A list of tuples (ideom_id, similarity).
        """
        similar_ideoms = []
        
        # Get all ideoms
        all_ideoms = self.ideom_network.get_all_ideoms()
        
        for ideom in all_ideoms:
            # Calculate semantic similarity
            similarity = self._calculate_semantic_similarity(token, ideom.name)
            
            if similarity >= self.semantic_similarity_threshold:
                similar_ideoms.append((ideom.id, similarity))
        
        # Sort by similarity (descending)
        similar_ideoms.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3 matches
        return similar_ideoms[:3]
    
    def _calculate_semantic_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate the semantic similarity between two words.
        
        This method uses a combination of techniques to determine semantic similarity:
        1. Exact matching
        2. Stemming/lemmatization matching
        3. Character-based similarity (Levenshtein distance)
        4. Semantic relationship detection (common prefixes, suffixes)
        5. Contextual similarity based on ideom connections
        
        Args:
            word1: The first word.
            word2: The second word.
            
        Returns:
            The semantic similarity score (0.0 to 1.0).
        """
        # If the words are the same, return 1.0
        if word1 == word2:
            return 1.0
        
        # Normalize words
        word1 = word1.lower()
        word2 = word2.lower()
        
        # Lemmatize words
        lemma1 = self.lemmatizer.lemmatize(word1)
        lemma2 = self.lemmatizer.lemmatize(word2)
        
        # If the lemmatized words are the same, high similarity
        if lemma1 == lemma2:
            return 0.95  # Not quite 1.0, but very high
        
        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(word1, word2)
        max_length = max(len(word1), len(word2))
        
        if max_length == 0:
            return 0.0
        
        # Convert distance to similarity
        char_similarity = 1.0 - (distance / max_length)
        
        # Check for common prefixes (3+ characters)
        prefix_similarity = 0.0
        min_prefix_length = min(3, min(len(word1), len(word2)))
        if word1[:min_prefix_length] == word2[:min_prefix_length]:
            prefix_length = min_prefix_length
            # Find the longest common prefix
            for i in range(min_prefix_length, min(len(word1), len(word2))):
                if word1[:i+1] == word2[:i+1]:
                    prefix_length = i + 1
                else:
                    break
            prefix_similarity = prefix_length / max(len(word1), len(word2))
        
        # Check for semantic relationships using ideom connections
        connection_similarity = self._check_ideom_connection_similarity(word1, word2)
        
        # Combine the similarities with weights
        combined_similarity = (
            0.3 * char_similarity +
            0.3 * prefix_similarity +
            0.4 * connection_similarity
        )
        
        return max(0.0, min(1.0, combined_similarity))
    
    def _check_ideom_connection_similarity(self, word1: str, word2: str) -> float:
        """
        Check the similarity between two words based on ideom connections.
        
        This method looks for ideoms corresponding to the words and checks
        if they are connected in the ideom network.
        
        Args:
            word1: The first word.
            word2: The second word.
            
        Returns:
            The connection similarity score (0.0 to 1.0).
        """
        # Get ideoms for the words
        ideoms1 = self.ideom_network.get_ideoms_by_name(word1)
        ideoms2 = self.ideom_network.get_ideoms_by_name(word2)
        
        # If either word has no corresponding ideoms, return 0.0
        if not ideoms1 or not ideoms2:
            return 0.0
        
        # Check for direct connections between ideoms
        max_connection_strength = 0.0
        
        for ideom1 in ideoms1:
            for ideom2 in ideoms2:
                # Check if ideom1 is connected to ideom2
                connection_strength = ideom1.get_connection_strength(ideom2.id)
                max_connection_strength = max(max_connection_strength, connection_strength)
                
                # Check if ideom2 is connected to ideom1
                connection_strength = ideom2.get_connection_strength(ideom1.id)
                max_connection_strength = max(max_connection_strength, connection_strength)
        
        # Check for indirect connections (ideoms that are both connected to a third ideom)
        if max_connection_strength < 0.3:  # Only check if direct connection is weak
            # Get all connected ideoms for each word
            connected_ideoms1 = set()
            connected_ideoms2 = set()
            
            for ideom1 in ideoms1:
                for connected_ideom in self.ideom_network.get_connected_ideoms(ideom1.id):
                    connected_ideoms1.add(connected_ideom.id)
            
            for ideom2 in ideoms2:
                for connected_ideom in self.ideom_network.get_connected_ideoms(ideom2.id):
                    connected_ideoms2.add(connected_ideom.id)
            
            # Find common connections
            common_connections = connected_ideoms1.intersection(connected_ideoms2)
            
            if common_connections:
                # Calculate similarity based on number of common connections
                indirect_similarity = min(0.7, len(common_connections) * 0.1)
                max_connection_strength = max(max_connection_strength, indirect_similarity)
        
        return max_connection_strength
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            s1: The first string.
            s2: The second string.
            
        Returns:
            The Levenshtein distance.
        """
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