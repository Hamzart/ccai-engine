"""
SemanticSimilarity module for the Knowledge Graph.

This module defines the SemanticSimilarity class, which calculates semantic similarity
between concepts, properties, and values in the knowledge graph of the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Dict, Tuple, Optional, Any, Set, Callable
import math
from dataclasses import dataclass, field
from .concept_node import ConceptNode


@dataclass
class SemanticSimilarity:
    """
    Calculates semantic similarity between concepts.
    
    The SemanticSimilarity class provides methods for calculating semantic similarity
    between concepts, properties, and values in the knowledge graph.
    
    Attributes:
        embedding_dimension: The dimension of the embedding vectors.
        embedding_cache: A cache of embedding vectors for concept names and property values.
        similarity_cache: A cache of similarity scores between concepts.
        embedding_function: A function that generates embedding vectors for text.
    """
    
    embedding_dimension: int = 256
    embedding_cache: Dict[str, List[float]] = field(default_factory=dict)
    similarity_cache: Dict[Tuple[str, str], float] = field(default_factory=dict)
    embedding_function: Optional[Callable[[str], List[float]]] = None
    
    def set_embedding_function(self, func: Callable[[str], List[float]]) -> None:
        """
        Set the embedding function.
        
        Args:
            func: A function that generates embedding vectors for text.
        """
        self.embedding_function = func
        # Clear the caches when the embedding function changes
        self.embedding_cache.clear()
        self.similarity_cache.clear()
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding vector for a text.
        
        Args:
            text: The text to get the embedding for.
            
        Returns:
            The embedding vector for the text.
            
        Raises:
            ValueError: If no embedding function has been set.
        """
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if self.embedding_function is None:
            # If no embedding function is set, use a simple fallback
            # This is just a placeholder and should be replaced with a proper embedding function
            embedding = self._fallback_embedding(text)
        else:
            embedding = self.embedding_function(text)
        
        self.embedding_cache[text] = embedding
        return embedding
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """
        A fallback embedding function.
        
        This is a simple fallback embedding function that generates a random vector
        based on the hash of the text. It should only be used when no proper embedding
        function has been set.
        
        Args:
            text: The text to get the embedding for.
            
        Returns:
            A random embedding vector for the text.
        """
        import hashlib
        import random
        
        # Use the hash of the text as a seed for the random number generator
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # Generate a random vector with the specified dimension
        embedding = [random.uniform(-1.0, 1.0) for _ in range(self.embedding_dimension)]
        
        # Normalize the vector
        magnitude = math.sqrt(sum(x**2 for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate the cosine similarity between two vectors.
        
        Args:
            vec1: The first vector.
            vec2: The second vector.
            
        Returns:
            The cosine similarity between the vectors.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(x**2 for x in vec1))
        magnitude2 = math.sqrt(sum(x**2 for x in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate the Euclidean distance between two vectors.
        
        Args:
            vec1: The first vector.
            vec2: The second vector.
            
        Returns:
            The Euclidean distance between the vectors.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        return math.sqrt(sum((a - b)**2 for a, b in zip(vec1, vec2)))
    
    def text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the semantic similarity between two texts.
        
        Args:
            text1: The first text.
            text2: The second text.
            
        Returns:
            The semantic similarity between the texts.
        """
        # Check the cache first
        cache_key = (text1, text2) if text1 <= text2 else (text2, text1)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Calculate the similarity
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        similarity = self.cosine_similarity(embedding1, embedding2)
        
        # Cache the result
        self.similarity_cache[cache_key] = similarity
        
        return similarity
    
    def concept_similarity(self, concept1: ConceptNode, concept2: ConceptNode) -> float:
        """
        Calculate the semantic similarity between two concepts.
        
        Args:
            concept1: The first concept.
            concept2: The second concept.
            
        Returns:
            The semantic similarity between the concepts.
        """
        # Check the cache first
        cache_key = (concept1.get_id(), concept2.get_id())
        reverse_cache_key = (concept2.get_id(), concept1.get_id())
        
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        if reverse_cache_key in self.similarity_cache:
            return self.similarity_cache[reverse_cache_key]
        
        # Calculate the similarity based on the concept names
        name_similarity = self.text_similarity(concept1.get_name(), concept2.get_name())
        
        # Calculate the similarity based on the concept properties
        property_similarity = self._calculate_property_similarity(concept1, concept2)
        
        # Calculate the similarity based on the concept categories
        category_similarity = self._calculate_category_similarity(concept1, concept2)
        
        # Calculate the similarity based on the concept relations
        relation_similarity = self._calculate_relation_similarity(concept1, concept2)
        
        # Combine the similarities with weights
        weights = [0.3, 0.3, 0.2, 0.2]  # Adjust these weights as needed
        similarity = (
            weights[0] * name_similarity +
            weights[1] * property_similarity +
            weights[2] * category_similarity +
            weights[3] * relation_similarity
        )
        
        # Cache the result
        self.similarity_cache[cache_key] = similarity
        
        return similarity
    
    def _calculate_property_similarity(self, concept1: ConceptNode, concept2: ConceptNode) -> float:
        """
        Calculate the similarity between the properties of two concepts.
        
        Args:
            concept1: The first concept.
            concept2: The second concept.
            
        Returns:
            The similarity between the properties of the concepts.
        """
        properties1 = concept1.get_properties()
        properties2 = concept2.get_properties()
        
        if not properties1 or not properties2:
            return 0.0
        
        # Find the common property names
        common_names = set(properties1.keys()) & set(properties2.keys())
        
        if not common_names:
            return 0.0
        
        # Calculate the similarity for each common property
        similarities = []
        for name in common_names:
            value1 = properties1[name].get_value()
            value2 = properties2[name].get_value()
            similarity = self.text_similarity(value1, value2)
            similarities.append(similarity)
        
        # Return the average similarity
        return sum(similarities) / len(similarities)
    
    def _calculate_category_similarity(self, concept1: ConceptNode, concept2: ConceptNode) -> float:
        """
        Calculate the similarity between the categories of two concepts.
        
        Args:
            concept1: The first concept.
            concept2: The second concept.
            
        Returns:
            The similarity between the categories of the concepts.
        """
        categories1 = set(concept1.get_categories())
        categories2 = set(concept2.get_categories())
        
        if not categories1 or not categories2:
            return 0.0
        
        # Calculate the Jaccard similarity between the category sets
        intersection = len(categories1 & categories2)
        union = len(categories1 | categories2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_relation_similarity(self, concept1: ConceptNode, concept2: ConceptNode) -> float:
        """
        Calculate the similarity between the relations of two concepts.
        
        Args:
            concept1: The first concept.
            concept2: The second concept.
            
        Returns:
            The similarity between the relations of the concepts.
        """
        relation_types1 = set(concept1.get_relation_types())
        relation_types2 = set(concept2.get_relation_types())
        
        if not relation_types1 or not relation_types2:
            return 0.0
        
        # Calculate the Jaccard similarity between the relation type sets
        intersection = len(relation_types1 & relation_types2)
        union = len(relation_types1 | relation_types2)
        
        return intersection / union if union > 0 else 0.0
    
    def find_similar_concepts(self, concept: ConceptNode, candidates: List[ConceptNode],
                             threshold: float = 0.7, limit: int = 10) -> List[Tuple[ConceptNode, float]]:
        """
        Find concepts similar to a given concept.
        
        Args:
            concept: The concept to find similar concepts for.
            candidates: A list of candidate concepts to compare with.
            threshold: The minimum similarity score required.
            limit: The maximum number of similar concepts to return.
            
        Returns:
            A list of tuples, where each tuple contains a similar concept and its similarity score.
        """
        similarities = []
        
        for candidate in candidates:
            if candidate.get_id() == concept.get_id():
                continue
            
            similarity = self.concept_similarity(concept, candidate)
            
            if similarity >= threshold:
                similarities.append((candidate, similarity))
        
        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top 'limit' similar concepts
        return similarities[:limit]
    
    def find_similar_by_text(self, text: str, candidates: List[ConceptNode],
                            threshold: float = 0.7, limit: int = 10) -> List[Tuple[ConceptNode, float]]:
        """
        Find concepts similar to a given text.
        
        Args:
            text: The text to find similar concepts for.
            candidates: A list of candidate concepts to compare with.
            threshold: The minimum similarity score required.
            limit: The maximum number of similar concepts to return.
            
        Returns:
            A list of tuples, where each tuple contains a similar concept and its similarity score.
        """
        similarities = []
        
        for candidate in candidates:
            similarity = self.text_similarity(text, candidate.get_name())
            
            if similarity >= threshold:
                similarities.append((candidate, similarity))
        
        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top 'limit' similar concepts
        return similarities[:limit]
    
    def cluster_concepts(self, concepts: List[ConceptNode], threshold: float = 0.7) -> List[List[ConceptNode]]:
        """
        Cluster concepts based on their semantic similarity.
        
        Args:
            concepts: A list of concepts to cluster.
            threshold: The minimum similarity score required for two concepts to be in the same cluster.
            
        Returns:
            A list of clusters, where each cluster is a list of concepts.
        """
        if not concepts:
            return []
        
        # Initialize clusters with the first concept
        clusters = [[concepts[0]]]
        
        # Assign each remaining concept to a cluster or create a new one
        for concept in concepts[1:]:
            best_cluster = None
            best_similarity = 0.0
            
            # Find the best cluster for the concept
            for i, cluster in enumerate(clusters):
                # Calculate the average similarity to the concepts in the cluster
                similarities = [self.concept_similarity(concept, c) for c in cluster]
                avg_similarity = sum(similarities) / len(similarities)
                
                if avg_similarity > best_similarity and avg_similarity >= threshold:
                    best_cluster = i
                    best_similarity = avg_similarity
            
            if best_cluster is not None:
                # Add the concept to the best cluster
                clusters[best_cluster].append(concept)
            else:
                # Create a new cluster for the concept
                clusters.append([concept])
        
        return clusters
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the semantic similarity calculator.
        """
        return {
            "embedding_dimension": self.embedding_dimension,
            # Note: We don't serialize the caches or the embedding function
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SemanticSimilarity':
        """
        Create a SemanticSimilarity instance from a dictionary.
        
        Args:
            data: A dictionary representation of a semantic similarity calculator.
            
        Returns:
            A new SemanticSimilarity instance.
        """
        return cls(
            embedding_dimension=data.get("embedding_dimension", 256)
        )