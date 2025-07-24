"""
UncertaintyHandler module for the Knowledge Graph.

This module defines the UncertaintyHandler class, which manages uncertainty
in the knowledge graph of the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Dict, Tuple, Optional, Any, Union
import math
from dataclasses import dataclass
from .property_value import PropertyValue


@dataclass
class UncertaintyHandler:
    """
    Handles uncertainty in the knowledge graph.
    
    The UncertaintyHandler class provides methods for managing and reasoning
    with uncertain knowledge in the knowledge graph.
    
    Attributes:
        confidence_threshold: The minimum confidence score required for a fact to be considered reliable.
        conflict_threshold: The threshold for determining when two facts are in conflict.
    """
    
    confidence_threshold: float = 0.7
    conflict_threshold: float = 0.3
    
    def is_reliable(self, confidence: float) -> bool:
        """
        Check if a confidence score is considered reliable.
        
        Args:
            confidence: The confidence score to check.
            
        Returns:
            True if the confidence score is considered reliable, False otherwise.
        """
        return confidence >= self.confidence_threshold
    
    def combine_confidence_scores(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        """
        Combine multiple confidence scores.
        
        This method combines multiple confidence scores using a weighted average.
        
        Args:
            scores: A list of confidence scores to combine.
            weights: An optional list of weights for the scores. If not provided, all scores are weighted equally.
            
        Returns:
            The combined confidence score.
        """
        if not scores:
            return 0.0
        
        if weights is None:
            # Equal weights
            weights = [1.0] * len(scores)
        elif len(weights) != len(scores):
            raise ValueError("The number of weights must match the number of scores")
        
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return weighted_sum / total_weight
    
    def combine_property_values(self, values: List[PropertyValue]) -> PropertyValue:
        """
        Combine multiple property values.
        
        This method combines multiple property values, taking into account their confidence scores.
        
        Args:
            values: A list of PropertyValue instances to combine.
            
        Returns:
            A new PropertyValue instance with the combined value and confidence score.
        """
        if not values:
            return PropertyValue(value="", confidence=0.0)
        
        if len(values) == 1:
            return values[0]
        
        # Group values by their actual value
        value_groups: Dict[str, List[PropertyValue]] = {}
        for value in values:
            if value.get_value() not in value_groups:
                value_groups[value.get_value()] = []
            value_groups[value.get_value()].append(value)
        
        # Calculate the combined confidence score for each value
        combined_scores: Dict[str, float] = {}
        for value_str, value_list in value_groups.items():
            scores = [v.get_confidence() for v in value_list]
            combined_scores[value_str] = self.combine_confidence_scores(scores)
        
        # Find the value with the highest combined confidence score
        best_value, best_score = max(combined_scores.items(), key=lambda x: x[1])
        
        return PropertyValue(value=best_value, confidence=best_score)
    
    def are_values_in_conflict(self, value1: PropertyValue, value2: PropertyValue) -> bool:
        """
        Check if two property values are in conflict.
        
        Args:
            value1: The first PropertyValue instance.
            value2: The second PropertyValue instance.
            
        Returns:
            True if the values are in conflict, False otherwise.
        """
        # If the values are the same, they are not in conflict
        if value1.get_value() == value2.get_value():
            return False
        
        # If both values have high confidence, they are in conflict
        if (value1.get_confidence() >= self.confidence_threshold and
            value2.get_confidence() >= self.confidence_threshold):
            return True
        
        # If the difference in confidence is large, they are not in conflict
        confidence_diff = abs(value1.get_confidence() - value2.get_confidence())
        if confidence_diff >= self.conflict_threshold:
            return False
        
        # Otherwise, they are in conflict
        return True
    
    def resolve_conflict(self, value1: PropertyValue, value2: PropertyValue) -> PropertyValue:
        """
        Resolve a conflict between two property values.
        
        Args:
            value1: The first PropertyValue instance.
            value2: The second PropertyValue instance.
            
        Returns:
            A new PropertyValue instance with the resolved value and confidence score.
        """
        # If the values are not in conflict, return the one with higher confidence
        if not self.are_values_in_conflict(value1, value2):
            return value1 if value1.get_confidence() >= value2.get_confidence() else value2
        
        # If the values are in conflict, create a new value with reduced confidence
        if value1.get_confidence() >= value2.get_confidence():
            # Reduce the confidence of value1
            reduced_confidence = value1.get_confidence() * (1.0 - value2.get_confidence())
            return PropertyValue(value=value1.get_value(), confidence=reduced_confidence)
        else:
            # Reduce the confidence of value2
            reduced_confidence = value2.get_confidence() * (1.0 - value1.get_confidence())
            return PropertyValue(value=value2.get_value(), confidence=reduced_confidence)
    
    def calculate_bayesian_update(self, prior: float, likelihood: float, evidence: float) -> float:
        """
        Calculate a Bayesian update.
        
        This method calculates a Bayesian update for a confidence score,
        given a prior probability, a likelihood, and evidence.
        
        Args:
            prior: The prior probability.
            likelihood: The likelihood of the evidence given the hypothesis.
            evidence: The probability of the evidence.
            
        Returns:
            The updated confidence score.
        """
        if evidence == 0:
            return prior
        
        posterior = (prior * likelihood) / evidence
        return min(1.0, max(0.0, posterior))
    
    def update_confidence_with_evidence(self, confidence: float, evidence_confidence: float,
                                       evidence_supports: bool) -> float:
        """
        Update a confidence score with new evidence.
        
        Args:
            confidence: The current confidence score.
            evidence_confidence: The confidence score of the new evidence.
            evidence_supports: True if the evidence supports the fact, False if it contradicts it.
            
        Returns:
            The updated confidence score.
        """
        if evidence_supports:
            # Evidence supports the fact, increase confidence
            return min(1.0, confidence + (1.0 - confidence) * evidence_confidence)
        else:
            # Evidence contradicts the fact, decrease confidence
            return max(0.0, confidence - confidence * evidence_confidence)
    
    def calculate_confidence_interval(self, confidence: float, sample_size: int) -> Tuple[float, float]:
        """
        Calculate a confidence interval.
        
        This method calculates a confidence interval for a confidence score,
        given the sample size used to derive the score.
        
        Args:
            confidence: The confidence score.
            sample_size: The sample size used to derive the score.
            
        Returns:
            A tuple containing the lower and upper bounds of the confidence interval.
        """
        if sample_size <= 1:
            return (0.0, 1.0)
        
        # Calculate the standard error
        standard_error = math.sqrt((confidence * (1.0 - confidence)) / sample_size)
        
        # Calculate the 95% confidence interval (using 1.96 for the z-score)
        margin_of_error = 1.96 * standard_error
        
        lower_bound = max(0.0, confidence - margin_of_error)
        upper_bound = min(1.0, confidence + margin_of_error)
        
        return (lower_bound, upper_bound)
    
    def calculate_entropy(self, probabilities: List[float]) -> float:
        """
        Calculate the entropy of a probability distribution.
        
        Args:
            probabilities: A list of probabilities that sum to 1.0.
            
        Returns:
            The entropy of the probability distribution.
        """
        if not probabilities:
            return 0.0
        
        # Filter out zero probabilities to avoid log(0)
        non_zero_probs = [p for p in probabilities if p > 0.0]
        
        # Calculate the entropy
        entropy = -sum(p * math.log2(p) for p in non_zero_probs)
        
        return entropy
    
    def calculate_information_gain(self, prior_entropy: float, posterior_entropies: List[float],
                                  probabilities: List[float]) -> float:
        """
        Calculate the information gain.
        
        This method calculates the information gain from a prior entropy
        to a set of posterior entropies, weighted by their probabilities.
        
        Args:
            prior_entropy: The entropy of the prior distribution.
            posterior_entropies: A list of entropies for the posterior distributions.
            probabilities: A list of probabilities for the posterior distributions.
            
        Returns:
            The information gain.
        """
        if len(posterior_entropies) != len(probabilities):
            raise ValueError("The number of posterior entropies must match the number of probabilities")
        
        # Calculate the expected posterior entropy
        expected_posterior_entropy = sum(p * e for p, e in zip(probabilities, posterior_entropies))
        
        # Calculate the information gain
        information_gain = prior_entropy - expected_posterior_entropy
        
        return information_gain
    
    def calculate_confidence_from_evidence(self, evidence_list: List[Tuple[bool, float]]) -> float:
        """
        Calculate a confidence score from a list of evidence.
        
        Args:
            evidence_list: A list of tuples, where each tuple contains a boolean indicating
                          whether the evidence supports the fact, and a confidence score for the evidence.
            
        Returns:
            The calculated confidence score.
        """
        if not evidence_list:
            return 0.0
        
        # Start with a neutral confidence
        confidence = 0.5
        
        # Update the confidence with each piece of evidence
        for supports, evidence_confidence in evidence_list:
            confidence = self.update_confidence_with_evidence(confidence, evidence_confidence, supports)
        
        return confidence
    
    def combine_conflicting_evidence(self, evidence_for: List[float], evidence_against: List[float]) -> float:
        """
        Combine conflicting evidence.
        
        This method combines evidence for and against a fact to produce a single confidence score.
        
        Args:
            evidence_for: A list of confidence scores for evidence supporting the fact.
            evidence_against: A list of confidence scores for evidence contradicting the fact.
            
        Returns:
            The combined confidence score.
        """
        if not evidence_for and not evidence_against:
            return 0.5  # Neutral confidence
        
        # Calculate the combined confidence for supporting evidence
        if evidence_for:
            combined_for = self.combine_confidence_scores(evidence_for)
        else:
            combined_for = 0.0
        
        # Calculate the combined confidence for contradicting evidence
        if evidence_against:
            combined_against = self.combine_confidence_scores(evidence_against)
        else:
            combined_against = 0.0
        
        # Calculate the final confidence score
        if combined_for == 0.0 and combined_against == 0.0:
            return 0.5  # Neutral confidence
        
        return combined_for / (combined_for + combined_against)
    
    def calculate_confidence_decay(self, confidence: float, time_elapsed: float, half_life: float) -> float:
        """
        Calculate confidence decay over time.
        
        This method calculates how a confidence score decays over time,
        using an exponential decay model.
        
        Args:
            confidence: The initial confidence score.
            time_elapsed: The time elapsed since the confidence score was established.
            half_life: The half-life of the confidence score.
            
        Returns:
            The decayed confidence score.
        """
        if time_elapsed <= 0 or half_life <= 0:
            return confidence
        
        # Calculate the decay factor
        decay_factor = math.exp(-math.log(2) * time_elapsed / half_life)
        
        # Calculate the decayed confidence
        decayed_confidence = 0.5 + (confidence - 0.5) * decay_factor
        
        return decayed_confidence
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the uncertainty handler.
        """
        return {
            "confidence_threshold": self.confidence_threshold,
            "conflict_threshold": self.conflict_threshold
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UncertaintyHandler':
        """
        Create an UncertaintyHandler instance from a dictionary.
        
        Args:
            data: A dictionary representation of an uncertainty handler.
            
        Returns:
            A new UncertaintyHandler instance.
        """
        return cls(
            confidence_threshold=data.get("confidence_threshold", 0.7),
            conflict_threshold=data.get("conflict_threshold", 0.3)
        )