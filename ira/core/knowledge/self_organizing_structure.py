"""
SelfOrganizingStructure module for the Knowledge Graph.

This module defines the SelfOrganizingStructure class, which dynamically organizes
and reorganizes the knowledge graph based on new information and learning.
"""

from typing import List, Dict, Tuple, Optional, Any, Set, Callable
import math
import random
from dataclasses import dataclass, field
from .concept_node import ConceptNode
from .semantic_similarity import SemanticSimilarity


@dataclass
class SelfOrganizingStructure:
    """
    Dynamically organizes the knowledge graph.
    
    The SelfOrganizingStructure class provides methods for dynamically organizing
    and reorganizing the knowledge graph based on new information and learning.
    
    Attributes:
        semantic_similarity: The semantic similarity calculator.
        reorganization_threshold: The threshold for triggering reorganization.
        max_cluster_size: The maximum size of a cluster.
        min_cluster_size: The minimum size of a cluster.
        stability_factor: A factor that controls the stability of the structure.
    """
    
    semantic_similarity: SemanticSimilarity
    reorganization_threshold: float = 0.5
    max_cluster_size: int = 100
    min_cluster_size: int = 5
    stability_factor: float = 0.8
    
    # Internal state
    _clusters: List[List[str]] = field(default_factory=list)
    _concept_to_cluster: Dict[str, int] = field(default_factory=dict)
    _cluster_centroids: Dict[int, List[float]] = field(default_factory=dict)
    _stability_scores: Dict[int, float] = field(default_factory=dict)
    _reorganization_count: int = 0
    
    def initialize(self, concepts: List[ConceptNode]) -> None:
        """
        Initialize the structure with a set of concepts.
        
        Args:
            concepts: A list of concepts to initialize the structure with.
        """
        if not concepts:
            return
        
        # Cluster the concepts
        concept_clusters = self.semantic_similarity.cluster_concepts(
            concepts, threshold=self.reorganization_threshold
        )
        
        # Reset the internal state
        self._clusters = []
        self._concept_to_cluster = {}
        self._cluster_centroids = {}
        self._stability_scores = {}
        
        # Initialize the clusters
        for i, cluster in enumerate(concept_clusters):
            cluster_ids = [concept.get_id() for concept in cluster]
            self._clusters.append(cluster_ids)
            
            for concept_id in cluster_ids:
                self._concept_to_cluster[concept_id] = i
            
            # Calculate the cluster centroid
            self._calculate_cluster_centroid(i, cluster)
            
            # Initialize the stability score
            self._stability_scores[i] = 1.0
    
    def _calculate_cluster_centroid(self, cluster_index: int, concepts: List[ConceptNode]) -> None:
        """
        Calculate the centroid of a cluster.
        
        Args:
            cluster_index: The index of the cluster.
            concepts: The concepts in the cluster.
        """
        if not concepts:
            return
        
        # Get the embeddings for all concept names
        embeddings = [self.semantic_similarity.get_embedding(concept.get_name()) for concept in concepts]
        
        # Calculate the centroid
        centroid = []
        for i in range(len(embeddings[0])):
            centroid.append(sum(embedding[i] for embedding in embeddings) / len(embeddings))
        
        # Normalize the centroid
        magnitude = math.sqrt(sum(x**2 for x in centroid))
        if magnitude > 0:
            centroid = [x / magnitude for x in centroid]
        
        self._cluster_centroids[cluster_index] = centroid
    
    def get_cluster_for_concept(self, concept_id: str) -> Optional[int]:
        """
        Get the cluster index for a concept.
        
        Args:
            concept_id: The ID of the concept.
            
        Returns:
            The index of the cluster containing the concept, or None if the concept is not in any cluster.
        """
        return self._concept_to_cluster.get(concept_id)
    
    def get_concepts_in_cluster(self, cluster_index: int) -> List[str]:
        """
        Get the concepts in a cluster.
        
        Args:
            cluster_index: The index of the cluster.
            
        Returns:
            A list of concept IDs in the cluster.
        """
        if cluster_index < 0 or cluster_index >= len(self._clusters):
            return []
        
        return self._clusters[cluster_index].copy()
    
    def get_all_clusters(self) -> List[List[str]]:
        """
        Get all clusters.
        
        Returns:
            A list of all clusters, where each cluster is a list of concept IDs.
        """
        return [cluster.copy() for cluster in self._clusters]
    
    def get_cluster_count(self) -> int:
        """
        Get the number of clusters.
        
        Returns:
            The number of clusters.
        """
        return len(self._clusters)
    
    def get_cluster_stability(self, cluster_index: int) -> float:
        """
        Get the stability score of a cluster.
        
        Args:
            cluster_index: The index of the cluster.
            
        Returns:
            The stability score of the cluster.
        """
        if cluster_index < 0 or cluster_index >= len(self._clusters):
            return 0.0
        
        return self._stability_scores.get(cluster_index, 0.0)
    
    def add_concept(self, concept: ConceptNode, concepts_by_id: Dict[str, ConceptNode]) -> bool:
        """
        Add a concept to the structure.
        
        Args:
            concept: The concept to add.
            concepts_by_id: A dictionary mapping concept IDs to ConceptNode instances.
            
        Returns:
            True if the concept was added to an existing cluster, False if a new cluster was created.
        """
        concept_id = concept.get_id()
        
        # If the concept is already in a cluster, remove it first
        if concept_id in self._concept_to_cluster:
            self.remove_concept(concept_id)
        
        # Find the best cluster for the concept
        best_cluster = None
        best_similarity = 0.0
        
        for i, cluster_ids in enumerate(self._clusters):
            # Skip clusters that are already at the maximum size
            if len(cluster_ids) >= self.max_cluster_size:
                continue
            
            # Calculate the similarity to the cluster centroid
            concept_embedding = self.semantic_similarity.get_embedding(concept.get_name())
            centroid = self._cluster_centroids.get(i)
            
            if centroid is not None:
                similarity = self.semantic_similarity.cosine_similarity(concept_embedding, centroid)
                
                if similarity > best_similarity and similarity >= self.reorganization_threshold:
                    best_cluster = i
                    best_similarity = similarity
        
        if best_cluster is not None:
            # Add the concept to the best cluster
            self._clusters[best_cluster].append(concept_id)
            self._concept_to_cluster[concept_id] = best_cluster
            
            # Update the cluster centroid
            cluster_concepts = [concepts_by_id[cid] for cid in self._clusters[best_cluster] if cid in concepts_by_id]
            self._calculate_cluster_centroid(best_cluster, cluster_concepts)
            
            # Decrease the stability score of the cluster
            self._stability_scores[best_cluster] *= self.stability_factor
            
            return True
        else:
            # Create a new cluster for the concept
            new_cluster_index = len(self._clusters)
            self._clusters.append([concept_id])
            self._concept_to_cluster[concept_id] = new_cluster_index
            
            # Calculate the cluster centroid
            self._cluster_centroids[new_cluster_index] = self.semantic_similarity.get_embedding(concept.get_name())
            
            # Initialize the stability score
            self._stability_scores[new_cluster_index] = 1.0
            
            return False
    
    def remove_concept(self, concept_id: str) -> bool:
        """
        Remove a concept from the structure.
        
        Args:
            concept_id: The ID of the concept to remove.
            
        Returns:
            True if the concept was removed, False if it was not in any cluster.
        """
        cluster_index = self._concept_to_cluster.get(concept_id)
        
        if cluster_index is None:
            return False
        
        # Remove the concept from the cluster
        self._clusters[cluster_index].remove(concept_id)
        del self._concept_to_cluster[concept_id]
        
        # If the cluster is now empty, remove it
        if not self._clusters[cluster_index]:
            # Remove the cluster
            self._clusters.pop(cluster_index)
            del self._cluster_centroids[cluster_index]
            del self._stability_scores[cluster_index]
            
            # Update the cluster indices for all concepts
            for cid, idx in list(self._concept_to_cluster.items()):
                if idx > cluster_index:
                    self._concept_to_cluster[cid] = idx - 1
            
            # Update the cluster indices for the centroids and stability scores
            for idx in range(cluster_index, len(self._clusters)):
                if idx + 1 in self._cluster_centroids:
                    self._cluster_centroids[idx] = self._cluster_centroids.pop(idx + 1)
                if idx + 1 in self._stability_scores:
                    self._stability_scores[idx] = self._stability_scores.pop(idx + 1)
        
        return True
    
    def update_concept(self, concept: ConceptNode, concepts_by_id: Dict[str, ConceptNode]) -> bool:
        """
        Update a concept in the structure.
        
        Args:
            concept: The updated concept.
            concepts_by_id: A dictionary mapping concept IDs to ConceptNode instances.
            
        Returns:
            True if the concept was updated, False if it was not in any cluster.
        """
        concept_id = concept.get_id()
        cluster_index = self._concept_to_cluster.get(concept_id)
        
        if cluster_index is None:
            return False
        
        # Update the cluster centroid
        cluster_concepts = [concepts_by_id[cid] for cid in self._clusters[cluster_index] if cid in concepts_by_id]
        self._calculate_cluster_centroid(cluster_index, cluster_concepts)
        
        # Check if the concept still belongs in the cluster
        concept_embedding = self.semantic_similarity.get_embedding(concept.get_name())
        centroid = self._cluster_centroids.get(cluster_index)
        
        if centroid is not None:
            similarity = self.semantic_similarity.cosine_similarity(concept_embedding, centroid)
            
            if similarity < self.reorganization_threshold:
                # The concept no longer belongs in the cluster
                # Remove it and add it again to find a better cluster
                self.remove_concept(concept_id)
                self.add_concept(concept, concepts_by_id)
        
        return True
    
    def merge_clusters(self, cluster1_index: int, cluster2_index: int, concepts_by_id: Dict[str, ConceptNode]) -> bool:
        """
        Merge two clusters.
        
        Args:
            cluster1_index: The index of the first cluster.
            cluster2_index: The index of the second cluster.
            concepts_by_id: A dictionary mapping concept IDs to ConceptNode instances.
            
        Returns:
            True if the clusters were merged, False if either cluster does not exist.
        """
        if (cluster1_index < 0 or cluster1_index >= len(self._clusters) or
            cluster2_index < 0 or cluster2_index >= len(self._clusters)):
            return False
        
        # Ensure cluster1_index < cluster2_index
        if cluster1_index > cluster2_index:
            cluster1_index, cluster2_index = cluster2_index, cluster1_index
        
        # Merge the clusters
        merged_cluster = self._clusters[cluster1_index] + self._clusters[cluster2_index]
        
        # Update the cluster for all concepts in the second cluster
        for concept_id in self._clusters[cluster2_index]:
            self._concept_to_cluster[concept_id] = cluster1_index
        
        # Update the first cluster
        self._clusters[cluster1_index] = merged_cluster
        
        # Remove the second cluster
        self._clusters.pop(cluster2_index)
        del self._cluster_centroids[cluster2_index]
        del self._stability_scores[cluster2_index]
        
        # Update the cluster indices for all concepts
        for cid, idx in list(self._concept_to_cluster.items()):
            if idx > cluster2_index:
                self._concept_to_cluster[cid] = idx - 1
        
        # Update the cluster indices for the centroids and stability scores
        for idx in range(cluster2_index, len(self._clusters)):
            if idx + 1 in self._cluster_centroids:
                self._cluster_centroids[idx] = self._cluster_centroids.pop(idx + 1)
            if idx + 1 in self._stability_scores:
                self._stability_scores[idx] = self._stability_scores.pop(idx + 1)
        
        # Calculate the new cluster centroid
        cluster_concepts = [concepts_by_id[cid] for cid in merged_cluster if cid in concepts_by_id]
        self._calculate_cluster_centroid(cluster1_index, cluster_concepts)
        
        # Update the stability score
        self._stability_scores[cluster1_index] = min(
            self._stability_scores.get(cluster1_index, 1.0),
            self._stability_scores.get(cluster2_index, 1.0)
        ) * self.stability_factor
        
        return True
    
    def split_cluster(self, cluster_index: int, concepts_by_id: Dict[str, ConceptNode]) -> bool:
        """
        Split a cluster into two.
        
        Args:
            cluster_index: The index of the cluster to split.
            concepts_by_id: A dictionary mapping concept IDs to ConceptNode instances.
            
        Returns:
            True if the cluster was split, False if the cluster does not exist or is too small.
        """
        if cluster_index < 0 or cluster_index >= len(self._clusters):
            return False
        
        cluster_ids = self._clusters[cluster_index]
        
        # Don't split clusters that are too small
        if len(cluster_ids) < self.min_cluster_size * 2:
            return False
        
        # Get the concepts in the cluster
        cluster_concepts = [concepts_by_id[cid] for cid in cluster_ids if cid in concepts_by_id]
        
        if len(cluster_concepts) < self.min_cluster_size * 2:
            return False
        
        # Split the cluster using k-means with k=2
        centroids, clusters = self._kmeans(cluster_concepts, 2)
        
        if len(clusters) != 2:
            return False
        
        # Update the first cluster
        self._clusters[cluster_index] = [concept.get_id() for concept in clusters[0]]
        
        # Create a new cluster for the second part
        new_cluster_index = len(self._clusters)
        self._clusters.append([concept.get_id() for concept in clusters[1]])
        
        # Update the cluster for all concepts in the new cluster
        for concept_id in self._clusters[new_cluster_index]:
            self._concept_to_cluster[concept_id] = new_cluster_index
        
        # Calculate the new cluster centroids
        self._calculate_cluster_centroid(cluster_index, clusters[0])
        self._calculate_cluster_centroid(new_cluster_index, clusters[1])
        
        # Initialize the stability scores
        self._stability_scores[cluster_index] = self.stability_factor
        self._stability_scores[new_cluster_index] = self.stability_factor
        
        return True
    
    def _kmeans(self, concepts: List[ConceptNode], k: int, max_iterations: int = 100) -> Tuple[List[List[float]], List[List[ConceptNode]]]:
        """
        Perform k-means clustering on a set of concepts.
        
        Args:
            concepts: The concepts to cluster.
            k: The number of clusters.
            max_iterations: The maximum number of iterations.
            
        Returns:
            A tuple containing the centroids and the clusters.
        """
        if not concepts or len(concepts) < k:
            return [], []
        
        # Get the embeddings for all concept names
        embeddings = []
        for concept in concepts:
            embedding = self.semantic_similarity.get_embedding(concept.get_name())
            embeddings.append(embedding)
        
        # Initialize the centroids randomly
        centroid_indices = random.sample(range(len(concepts)), k)
        centroids = [embeddings[i] for i in centroid_indices]
        
        # Perform k-means clustering
        for _ in range(max_iterations):
            # Assign each concept to the nearest centroid
            clusters = [[] for _ in range(k)]
            cluster_embeddings = [[] for _ in range(k)]
            
            for i, (concept, embedding) in enumerate(zip(concepts, embeddings)):
                # Find the nearest centroid
                nearest_centroid = 0
                min_distance = float('inf')
                
                for j, centroid in enumerate(centroids):
                    distance = self.semantic_similarity.euclidean_distance(embedding, centroid)
                    
                    if distance < min_distance:
                        nearest_centroid = j
                        min_distance = distance
                
                # Assign the concept to the nearest centroid
                clusters[nearest_centroid].append(concept)
                cluster_embeddings[nearest_centroid].append(embedding)
            
            # Check if any cluster is empty
            if any(not cluster for cluster in clusters):
                # Reassign centroids and try again
                centroid_indices = random.sample(range(len(concepts)), k)
                centroids = [embeddings[i] for i in centroid_indices]
                continue
            
            # Calculate the new centroids
            new_centroids = []
            for cluster_embedding in cluster_embeddings:
                centroid = []
                for i in range(len(cluster_embedding[0])):
                    centroid.append(sum(embedding[i] for embedding in cluster_embedding) / len(cluster_embedding))
                
                # Normalize the centroid
                magnitude = math.sqrt(sum(x**2 for x in centroid))
                if magnitude > 0:
                    centroid = [x / magnitude for x in centroid]
                
                new_centroids.append(centroid)
            
            # Check for convergence
            converged = True
            for i, (old_centroid, new_centroid) in enumerate(zip(centroids, new_centroids)):
                if self.semantic_similarity.euclidean_distance(old_centroid, new_centroid) > 1e-6:
                    converged = False
                    break
            
            if converged:
                break
            
            centroids = new_centroids
        
        return centroids, clusters
    
    def reorganize(self, concepts_by_id: Dict[str, ConceptNode]) -> int:
        """
        Reorganize the structure.
        
        This method reorganizes the structure by merging similar clusters
        and splitting large clusters.
        
        Args:
            concepts_by_id: A dictionary mapping concept IDs to ConceptNode instances.
            
        Returns:
            The number of changes made during reorganization.
        """
        if not self._clusters:
            return 0
        
        changes = 0
        
        # Merge similar clusters
        for i in range(len(self._clusters)):
            if i >= len(self._clusters):
                break
            
            for j in range(i + 1, len(self._clusters)):
                if j >= len(self._clusters):
                    break
                
                # Calculate the similarity between the cluster centroids
                centroid_i = self._cluster_centroids.get(i)
                centroid_j = self._cluster_centroids.get(j)
                
                if centroid_i is not None and centroid_j is not None:
                    similarity = self.semantic_similarity.cosine_similarity(centroid_i, centroid_j)
                    
                    if similarity >= self.reorganization_threshold:
                        # Merge the clusters
                        if self.merge_clusters(i, j, concepts_by_id):
                            changes += 1
                            # Decrement j to account for the removed cluster
                            j -= 1
        
        # Split large clusters
        for i in range(len(self._clusters)):
            if len(self._clusters[i]) > self.max_cluster_size:
                if self.split_cluster(i, concepts_by_id):
                    changes += 1
        
        if changes > 0:
            self._reorganization_count += 1
        
        return changes
    
    def get_reorganization_count(self) -> int:
        """
        Get the number of times the structure has been reorganized.
        
        Returns:
            The number of times the structure has been reorganized.
        """
        return self._reorganization_count
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the self-organizing structure.
        """
        return {
            "reorganization_threshold": self.reorganization_threshold,
            "max_cluster_size": self.max_cluster_size,
            "min_cluster_size": self.min_cluster_size,
            "stability_factor": self.stability_factor,
            "clusters": self._clusters,
            "concept_to_cluster": self._concept_to_cluster,
            "stability_scores": self._stability_scores,
            "reorganization_count": self._reorganization_count
        }
    
    @classmethod
    def from_dict(cls, data: dict, semantic_similarity: SemanticSimilarity) -> 'SelfOrganizingStructure':
        """
        Create a SelfOrganizingStructure instance from a dictionary.
        
        Args:
            data: A dictionary representation of a self-organizing structure.
            semantic_similarity: The semantic similarity calculator.
            
        Returns:
            A new SelfOrganizingStructure instance.
        """
        instance = cls(
            semantic_similarity=semantic_similarity,
            reorganization_threshold=data.get("reorganization_threshold", 0.5),
            max_cluster_size=data.get("max_cluster_size", 100),
            min_cluster_size=data.get("min_cluster_size", 5),
            stability_factor=data.get("stability_factor", 0.8)
        )
        
        instance._clusters = data.get("clusters", [])
        instance._concept_to_cluster = data.get("concept_to_cluster", {})
        instance._stability_scores = data.get("stability_scores", {})
        instance._reorganization_count = data.get("reorganization_count", 0)
        
        # Rebuild the cluster centroids
        instance._cluster_centroids = {}
        
        return instance