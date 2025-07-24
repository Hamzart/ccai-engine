"""
AdvancedPrefabMatcher module for the Unified Reasoning Core.

This module defines the AdvancedPrefabMatcher class, which extends the PrefabManager
with more sophisticated prefab matching capabilities in the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Dict, Set, Tuple, Optional
from .prefab_manager import PrefabManager
from .prefab import Prefab
from .activation_pattern import ActivationPattern
from .ideom_network import IdeomNetwork


class AdvancedPrefabMatcher:
    """
    An advanced matcher for prefabs in the Unified Reasoning Core.
    
    The AdvancedPrefabMatcher extends the PrefabManager with more sophisticated
    prefab matching capabilities, including partial matches, combinations,
    and context-aware matching.
    
    Attributes:
        prefab_manager: The underlying PrefabManager.
        ideom_network: The ideom network for semantic matching.
        partial_match_threshold: The threshold for considering a partial match.
        combination_threshold: The threshold for considering a combination match.
    """
    
    def __init__(
        self,
        prefab_manager: PrefabManager,
        ideom_network: IdeomNetwork,
        partial_match_threshold: float = 0.6,
        combination_threshold: float = 0.7
    ):
        """
        Initialize an advanced prefab matcher.
        
        Args:
            prefab_manager: The underlying PrefabManager.
            ideom_network: The ideom network for semantic matching.
            partial_match_threshold: The threshold for considering a partial match.
            combination_threshold: The threshold for considering a combination match.
        """
        self.prefab_manager = prefab_manager
        self.ideom_network = ideom_network
        self.partial_match_threshold = partial_match_threshold
        self.combination_threshold = combination_threshold
    
    def find_matching_prefabs(
        self,
        activation_pattern: ActivationPattern,
        include_partial_matches: bool = True,
        include_combinations: bool = True
    ) -> List[Prefab]:
        """
        Find prefabs that match the given activation pattern.
        
        This method extends the basic prefab matching with partial matches
        and combinations of prefabs.
        
        Args:
            activation_pattern: The activation pattern to match against.
            include_partial_matches: Whether to include partial matches.
            include_combinations: Whether to include combinations of prefabs.
            
        Returns:
            A list of Prefab instances that match the activation pattern, sorted by activation level.
        """
        # Get exact matches from the prefab manager
        exact_matches = self.prefab_manager.find_matching_prefabs(activation_pattern)
        
        # If we don't need partial matches or combinations, return exact matches
        if not include_partial_matches and not include_combinations:
            return exact_matches
        
        # Find partial matches if requested
        partial_matches = []
        if include_partial_matches:
            partial_matches = self._find_partial_matches(activation_pattern)
        
        # Find combinations if requested
        combination_matches = []
        if include_combinations:
            combination_matches = self._find_combinations(activation_pattern, exact_matches)
        
        # Combine all matches
        all_matches = exact_matches + partial_matches + combination_matches
        
        # Remove duplicates (by prefab ID)
        unique_matches = {}
        for prefab in all_matches:
            if prefab.id not in unique_matches or prefab.activation_level > unique_matches[prefab.id].activation_level:
                unique_matches[prefab.id] = prefab
        
        # Sort by activation level in descending order
        sorted_matches = sorted(
            unique_matches.values(),
            key=lambda p: p.activation_level,
            reverse=True
        )
        
        return sorted_matches
    
    def _find_partial_matches(self, activation_pattern: ActivationPattern) -> List[Prefab]:
        """
        Find prefabs that partially match the given activation pattern.
        
        Args:
            activation_pattern: The activation pattern to match against.
            
        Returns:
            A list of Prefab instances that partially match the activation pattern.
        """
        partial_matches = []
        
        # Get all prefabs
        all_prefabs = self.prefab_manager.get_all_prefabs()
        
        # Get the active ideoms from the activation pattern
        active_ideoms = activation_pattern.get_active_ideoms()
        
        for prefab in all_prefabs:
            # Calculate the match score
            match_score = self._calculate_partial_match_score(prefab, activation_pattern, active_ideoms)
            
            # If the match score is above the threshold, activate the prefab
            if match_score >= self.partial_match_threshold:
                # Create a new prefab with the match score as the activation level
                activated_prefab = Prefab(
                    id=prefab.id,
                    name=prefab.name,
                    ideom_weights=prefab.ideom_weights,
                    activation_level=match_score,
                    activation_threshold=prefab.activation_threshold,
                    response_template=prefab.response_template,
                    tags=prefab.tags
                )
                
                partial_matches.append(activated_prefab)
        
        return partial_matches
    
    def _calculate_partial_match_score(
        self,
        prefab: Prefab,
        activation_pattern: ActivationPattern,
        active_ideoms: Set[str]
    ) -> float:
        """
        Calculate the partial match score for a prefab.
        
        Args:
            prefab: The prefab to calculate the score for.
            activation_pattern: The activation pattern to match against.
            active_ideoms: The set of active ideom IDs in the activation pattern.
            
        Returns:
            The partial match score (0.0 to 1.0).
        """
        # Get the ideom weights from the prefab
        prefab_ideoms = set(prefab.ideom_weights.keys())
        
        # Calculate the overlap between the prefab ideoms and the active ideoms
        overlap = prefab_ideoms.intersection(active_ideoms)
        
        # If there's no overlap, return 0.0
        if not overlap:
            return 0.0
        
        # Calculate the weighted match score
        weighted_sum = 0.0
        total_weight = 0.0
        
        for ideom_id in overlap:
            prefab_weight = prefab.ideom_weights[ideom_id]
            activation = activation_pattern.get_activation_level(ideom_id)
            weighted_sum += prefab_weight * activation
            total_weight += prefab_weight
        
        # Normalize by the total weight
        if total_weight > 0:
            weighted_score = weighted_sum / total_weight
        else:
            weighted_score = 0.0
        
        # Calculate the coverage score (how much of the prefab is covered)
        coverage = len(overlap) / len(prefab_ideoms)
        
        # Combine the weighted score and coverage
        return (weighted_score + coverage) / 2
    
    def _find_combinations(
        self,
        activation_pattern: ActivationPattern,
        exact_matches: List[Prefab]
    ) -> List[Prefab]:
        """
        Find combinations of prefabs that match the given activation pattern.
        
        Args:
            activation_pattern: The activation pattern to match against.
            exact_matches: The list of exact matches to exclude from combinations.
            
        Returns:
            A list of Prefab instances representing combinations.
        """
        combinations = []
        
        # Get all prefabs
        all_prefabs = self.prefab_manager.get_all_prefabs()
        
        # Get the IDs of exact matches to exclude them from combinations
        exact_match_ids = {prefab.id for prefab in exact_matches}
        
        # Get candidate prefabs (excluding exact matches)
        candidate_prefabs = [
            prefab for prefab in all_prefabs
            if prefab.id not in exact_match_ids
        ]
        
        # If there are fewer than 2 candidates, return an empty list
        if len(candidate_prefabs) < 2:
            return combinations
        
        # Try all pairs of prefabs
        for i in range(len(candidate_prefabs)):
            for j in range(i + 1, len(candidate_prefabs)):
                prefab1 = candidate_prefabs[i]
                prefab2 = candidate_prefabs[j]
                
                # Calculate the combination score
                combination_score = self._calculate_combination_score(
                    prefab1, prefab2, activation_pattern
                )
                
                # If the combination score is above the threshold, create a combined prefab
                if combination_score >= self.combination_threshold:
                    combined_prefab = self._create_combined_prefab(
                        prefab1, prefab2, combination_score
                    )
                    combinations.append(combined_prefab)
        
        return combinations
    
    def _calculate_combination_score(
        self,
        prefab1: Prefab,
        prefab2: Prefab,
        activation_pattern: ActivationPattern
    ) -> float:
        """
        Calculate the combination score for two prefabs.
        
        Args:
            prefab1: The first prefab.
            prefab2: The second prefab.
            activation_pattern: The activation pattern to match against.
            
        Returns:
            The combination score (0.0 to 1.0).
        """
        # Get the ideom weights from the prefabs
        ideom_weights1 = prefab1.ideom_weights
        ideom_weights2 = prefab2.ideom_weights
        
        # Get the union of ideom IDs
        all_ideom_ids = set(ideom_weights1.keys()).union(set(ideom_weights2.keys()))
        
        # Calculate the weighted match score
        weighted_sum = 0.0
        total_weight = 0.0
        
        for ideom_id in all_ideom_ids:
            # Get the weight from each prefab (0.0 if not present)
            weight1 = ideom_weights1.get(ideom_id, 0.0)
            weight2 = ideom_weights2.get(ideom_id, 0.0)
            
            # Use the maximum weight
            weight = max(weight1, weight2)
            
            # Get the activation level
            activation = activation_pattern.get_activation_level(ideom_id)
            
            weighted_sum += weight * activation
            total_weight += weight
        
        # Normalize by the total weight
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.0
    
    def _create_combined_prefab(
        self,
        prefab1: Prefab,
        prefab2: Prefab,
        combination_score: float
    ) -> Prefab:
        """
        Create a combined prefab from two prefabs.
        
        Args:
            prefab1: The first prefab.
            prefab2: The second prefab.
            combination_score: The combination score.
            
        Returns:
            A new Prefab instance representing the combination.
        """
        import uuid
        
        # Generate a unique ID for the combined prefab
        combined_id = str(uuid.uuid4())
        
        # Combine the names
        combined_name = f"Combined: {prefab1.name} + {prefab2.name}"
        
        # Combine the ideom weights
        combined_weights = {}
        
        # Add weights from the first prefab
        for ideom_id, weight in prefab1.ideom_weights.items():
            combined_weights[ideom_id] = weight
        
        # Add or update weights from the second prefab
        for ideom_id, weight in prefab2.ideom_weights.items():
            if ideom_id in combined_weights:
                combined_weights[ideom_id] = max(combined_weights[ideom_id], weight)
            else:
                combined_weights[ideom_id] = weight
        
        # Combine the tags
        combined_tags = list(set(prefab1.tags + prefab2.tags))
        
        # Choose the response template from the prefab with more ideom weights
        if len(prefab1.ideom_weights) >= len(prefab2.ideom_weights):
            response_template = prefab1.response_template
        else:
            response_template = prefab2.response_template
        
        # Create the combined prefab
        return Prefab(
            id=combined_id,
            name=combined_name,
            ideom_weights=combined_weights,
            activation_level=combination_score,
            activation_threshold=min(prefab1.activation_threshold, prefab2.activation_threshold),
            response_template=response_template,
            tags=combined_tags
        )
    
    def get_semantic_matches(
        self,
        activation_pattern: ActivationPattern,
        semantic_threshold: float = 0.5
    ) -> List[Prefab]:
        """
        Find prefabs that semantically match the given activation pattern.
        
        Args:
            activation_pattern: The activation pattern to match against.
            semantic_threshold: The threshold for considering a semantic match.
            
        Returns:
            A list of Prefab instances that semantically match the activation pattern.
        """
        semantic_matches = []
        
        # Get all prefabs
        all_prefabs = self.prefab_manager.get_all_prefabs()
        
        # Get the active ideoms from the activation pattern
        active_ideoms = list(activation_pattern.get_active_ideoms())
        
        for prefab in all_prefabs:
            # Calculate the semantic match score
            match_score = self._calculate_semantic_match_score(prefab, active_ideoms)
            
            # If the match score is above the threshold, activate the prefab
            if match_score >= semantic_threshold:
                # Create a new prefab with the match score as the activation level
                activated_prefab = Prefab(
                    id=prefab.id,
                    name=prefab.name,
                    ideom_weights=prefab.ideom_weights,
                    activation_level=match_score,
                    activation_threshold=prefab.activation_threshold,
                    response_template=prefab.response_template,
                    tags=prefab.tags
                )
                
                semantic_matches.append(activated_prefab)
        
        return semantic_matches
    
    def _calculate_semantic_match_score(
        self,
        prefab: Prefab,
        active_ideoms: List[str]
    ) -> float:
        """
        Calculate the semantic match score for a prefab.
        
        Args:
            prefab: The prefab to calculate the score for.
            active_ideoms: The list of active ideom IDs.
            
        Returns:
            The semantic match score (0.0 to 1.0).
        """
        # Get the ideom weights from the prefab
        prefab_ideoms = list(prefab.ideom_weights.keys())
        
        # If there are no active ideoms or prefab ideoms, return 0.0
        if not active_ideoms or not prefab_ideoms:
            return 0.0
        
        # Calculate the semantic similarity between each active ideom and each prefab ideom
        total_similarity = 0.0
        max_similarities = []
        
        for active_id in active_ideoms:
            active_ideom = self.ideom_network.get_ideom(active_id)
            if active_ideom is None:
                continue
            
            # Find the most similar prefab ideom
            max_similarity = 0.0
            for prefab_id in prefab_ideoms:
                prefab_ideom = self.ideom_network.get_ideom(prefab_id)
                if prefab_ideom is None:
                    continue
                
                # Calculate the semantic similarity
                similarity = self._calculate_ideom_similarity(active_ideom, prefab_ideom)
                max_similarity = max(max_similarity, similarity)
            
            if max_similarity > 0.0:
                max_similarities.append(max_similarity)
        
        # If there are no similarities, return 0.0
        if not max_similarities:
            return 0.0
        
        # Return the average of the maximum similarities
        return sum(max_similarities) / len(max_similarities)
    
    def _calculate_ideom_similarity(self, ideom1, ideom2) -> float:
        """
        Calculate the semantic similarity between two ideoms.
        
        Args:
            ideom1: The first ideom.
            ideom2: The second ideom.
            
        Returns:
            The semantic similarity (0.0 to 1.0).
        """
        # If the ideoms are the same, return 1.0
        if ideom1.id == ideom2.id:
            return 1.0
        
        # Calculate the Jaccard similarity of their connections
        connections1 = set(ideom1.connections.keys())
        connections2 = set(ideom2.connections.keys())
        
        intersection = len(connections1.intersection(connections2))
        union = len(connections1.union(connections2))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Calculate the name similarity
        name_similarity = self._calculate_name_similarity(ideom1.name, ideom2.name)
        
        # Combine the similarities
        return (jaccard_similarity + name_similarity) / 2
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate the similarity between two ideom names.
        
        Args:
            name1: The first name.
            name2: The second name.
            
        Returns:
            The name similarity (0.0 to 1.0).
        """
        # If the names are the same, return 1.0
        if name1 == name2:
            return 1.0
        
        # Calculate the Levenshtein distance
        distance = self._levenshtein_distance(name1, name2)
        max_length = max(len(name1), len(name2))
        
        if max_length == 0:
            return 0.0
        
        # Convert distance to similarity
        return 1.0 - (distance / max_length)
    
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