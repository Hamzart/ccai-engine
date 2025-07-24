"""
Sentiment analysis module for CCAI chatbot.

This module provides functionality for analyzing the sentiment of user messages
and adjusting responses accordingly.
"""

import logging
import re
from typing import Dict, Any, Tuple, List, Optional
import math

# Set up logging
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes the sentiment of user messages.
    
    This class is responsible for:
    - Detecting the emotional tone of user messages
    - Identifying specific emotions (joy, anger, sadness, etc.)
    - Providing sentiment scores for adjusting responses
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        # Lexicons for different emotions
        self.emotion_lexicons = {
            "joy": [
                "happy", "glad", "delighted", "pleased", "excited", "thrilled",
                "enjoy", "love", "wonderful", "fantastic", "great", "excellent",
                "amazing", "awesome", "good", "positive", "joy", "joyful", "smile",
                "laugh", "fun", "celebrate", "congratulations", "yay", "hurray"
            ],
            "sadness": [
                "sad", "unhappy", "depressed", "miserable", "gloomy", "disappointed",
                "upset", "down", "heartbroken", "grief", "sorrow", "regret", "miss",
                "lonely", "alone", "cry", "tears", "weep", "despair", "hopeless"
            ],
            "anger": [
                "angry", "mad", "furious", "outraged", "annoyed", "irritated",
                "frustrated", "hate", "dislike", "resent", "hostile", "bitter",
                "enraged", "infuriated", "disgusted", "offended", "upset", "cross"
            ],
            "fear": [
                "afraid", "scared", "frightened", "terrified", "anxious", "worried",
                "nervous", "panic", "terror", "horror", "dread", "fear", "alarmed",
                "concerned", "uneasy", "apprehensive", "stressed", "distressed"
            ],
            "surprise": [
                "surprised", "amazed", "astonished", "shocked", "startled",
                "unexpected", "wow", "whoa", "gosh", "incredible", "unbelievable",
                "unexpected", "sudden", "wonder", "awe", "stunned"
            ],
            "disgust": [
                "disgusted", "revolted", "repulsed", "gross", "nasty", "yuck",
                "ew", "distaste", "aversion", "repugnant", "offensive", "foul",
                "sickening", "nauseous", "vile", "loathsome"
            ],
            "trust": [
                "trust", "believe", "faith", "confident", "reliable", "dependable",
                "honest", "loyal", "trustworthy", "credible", "authentic", "genuine",
                "sincere", "true", "certain", "sure", "respect", "admire"
            ],
            "anticipation": [
                "anticipate", "expect", "await", "looking forward", "hope", "eager",
                "excited", "anticipation", "suspense", "waiting", "soon", "future",
                "prospect", "potential", "possibility", "plan", "prepare"
            ]
        }
        
        # Intensity modifiers
        self.intensifiers = [
            "very", "extremely", "incredibly", "really", "so", "too",
            "absolutely", "completely", "totally", "utterly", "highly",
            "especially", "particularly", "exceptionally", "extraordinarily"
        ]
        
        self.diminishers = [
            "somewhat", "slightly", "a bit", "a little", "kind of", "sort of",
            "rather", "quite", "fairly", "pretty", "moderately", "relatively"
        ]
        
        # Negation words
        self.negations = [
            "not", "no", "never", "none", "nobody", "nothing", "nowhere",
            "neither", "nor", "hardly", "scarcely", "barely", "don't", "doesn't",
            "didn't", "won't", "wouldn't", "shouldn't", "couldn't", "can't", "isn't",
            "aren't", "wasn't", "weren't"
        ]
        
        # Punctuation impact
        self.punctuation_impact = {
            "!": 0.3,  # Exclamation marks intensify emotion
            "?": 0.1,  # Question marks slightly modify emotion
            "...": -0.1  # Ellipsis can indicate hesitation or uncertainty
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Normalize text
        text = text.lower()
        
        # Calculate emotion scores
        emotion_scores = self._calculate_emotion_scores(text)
        
        # Determine overall sentiment
        sentiment_score = self._calculate_sentiment_score(emotion_scores)
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else "neutral"
        
        # Check for mixed emotions
        emotions_above_threshold = [e for e, s in emotion_scores.items() if s > 0.3]
        is_mixed = len(emotions_above_threshold) > 1
        
        # Calculate intensity
        intensity = self._calculate_intensity(text, sentiment_score)
        
        return {
            "sentiment_score": sentiment_score,  # -1.0 to 1.0
            "dominant_emotion": dominant_emotion,
            "emotion_scores": emotion_scores,
            "is_mixed": is_mixed,
            "mixed_emotions": emotions_above_threshold if is_mixed else [],
            "intensity": intensity,  # 0.0 to 1.0
        }
    
    def _calculate_emotion_scores(self, text: str) -> Dict[str, float]:
        """Calculate scores for each emotion category."""
        scores = {emotion: 0.0 for emotion in self.emotion_lexicons}
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Track negation context
        negation_active = False
        
        for i, word in enumerate(words):
            # Check for negations
            if word in self.negations:
                negation_active = True
                continue
            
            # Negation context typically spans 3-4 words
            if i > 0 and words[i-1] in self.negations:
                negation_active = True
            
            # Reset negation after a few words
            if negation_active and i > 0 and i % 4 == 0:
                negation_active = False
            
            # Check intensifiers and diminishers
            intensifier_factor = 1.0
            for intensifier in self.intensifiers:
                if intensifier in " ".join(words[max(0, i-2):i]):
                    intensifier_factor = 1.5
                    break
            
            for diminisher in self.diminishers:
                if diminisher in " ".join(words[max(0, i-2):i]):
                    intensifier_factor = 0.5
                    break
            
            # Check each emotion lexicon
            for emotion, lexicon in self.emotion_lexicons.items():
                if word in lexicon:
                    # Apply negation if active
                    score_change = 0.2 * intensifier_factor
                    if negation_active:
                        # Negation inverts the emotion
                        opposite_emotions = {
                            "joy": "sadness",
                            "sadness": "joy",
                            "anger": "trust",
                            "fear": "trust",
                            "trust": "fear",
                            "disgust": "joy",
                            "surprise": "anticipation",
                            "anticipation": "surprise"
                        }
                        opposite = opposite_emotions.get(emotion, emotion)
                        scores[opposite] += score_change
                    else:
                        scores[emotion] += score_change
        
        # Check for punctuation
        for punct, impact in self.punctuation_impact.items():
            count = text.count(punct)
            if count > 0:
                # Apply punctuation impact to the dominant emotion
                dominant_emotion = max(scores.items(), key=lambda x: x[1])[0] if scores else None
                if dominant_emotion:
                    scores[dominant_emotion] += impact * min(count, 3)  # Cap at 3 occurrences
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            for emotion in scores:
                scores[emotion] /= total
        
        return scores
    
    def _calculate_sentiment_score(self, emotion_scores: Dict[str, float]) -> float:
        """Calculate overall sentiment score from emotion scores."""
        # Positive emotions contribute positively, negative emotions negatively
        positive_emotions = ["joy", "trust", "anticipation", "surprise"]
        negative_emotions = ["sadness", "anger", "fear", "disgust"]
        
        positive_score = sum(emotion_scores.get(e, 0) for e in positive_emotions)
        negative_score = sum(emotion_scores.get(e, 0) for e in negative_emotions)
        
        # Calculate overall sentiment (-1.0 to 1.0)
        if positive_score == 0 and negative_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / (positive_score + negative_score)
    
    def _calculate_intensity(self, text: str, sentiment_score: float) -> float:
        """Calculate the intensity of the emotion."""
        # Factors that contribute to intensity:
        # 1. Absolute value of sentiment score
        # 2. Presence of intensifiers
        # 3. Punctuation (especially exclamation marks)
        # 4. ALL CAPS words
        
        base_intensity = abs(sentiment_score)
        
        # Check for intensifiers
        intensifier_count = sum(text.lower().count(intensifier) for intensifier in self.intensifiers)
        intensifier_factor = min(intensifier_count * 0.1, 0.5)  # Cap at 0.5
        
        # Check for exclamation marks
        exclamation_count = text.count("!")
        exclamation_factor = min(exclamation_count * 0.1, 0.3)  # Cap at 0.3
        
        # Check for ALL CAPS words
        words = re.findall(r'\b[A-Z]{2,}\b', text)  # Words with 2+ uppercase letters
        caps_factor = min(len(words) * 0.1, 0.2)  # Cap at 0.2
        
        # Combine factors
        intensity = base_intensity + intensifier_factor + exclamation_factor + caps_factor
        
        # Ensure intensity is between 0 and 1
        return max(0.0, min(1.0, intensity))
    
    def get_response_adjustment(self, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get suggestions for adjusting the response based on sentiment.
        
        Args:
            sentiment_result: The result from analyze()
            
        Returns:
            Dictionary with response adjustment suggestions
        """
        score = sentiment_result["sentiment_score"]
        dominant_emotion = sentiment_result["dominant_emotion"]
        intensity = sentiment_result["intensity"]
        
        # Default adjustments
        adjustments = {
            "tone": "neutral",
            "empathy_level": "moderate",
            "formality": "moderate",
            "verbosity": "moderate",
            "suggested_phrases": []
        }
        
        # Adjust tone based on sentiment score
        if score > 0.5:
            adjustments["tone"] = "very positive"
        elif score > 0.2:
            adjustments["tone"] = "positive"
        elif score < -0.5:
            adjustments["tone"] = "very negative"
        elif score < -0.2:
            adjustments["tone"] = "negative"
        
        # Adjust empathy level based on emotion and intensity
        if dominant_emotion in ["sadness", "fear"] and intensity > 0.5:
            adjustments["empathy_level"] = "high"
            adjustments["suggested_phrases"].append("I understand this is difficult.")
        elif dominant_emotion == "anger" and intensity > 0.5:
            adjustments["empathy_level"] = "high"
            adjustments["suggested_phrases"].append("I understand your frustration.")
        elif dominant_emotion == "joy" and intensity > 0.5:
            adjustments["empathy_level"] = "moderate"
            adjustments["suggested_phrases"].append("That's wonderful to hear!")
        
        # Adjust formality based on emotion
        if dominant_emotion in ["joy", "surprise"]:
            adjustments["formality"] = "casual"
        elif dominant_emotion in ["anger", "disgust"]:
            adjustments["formality"] = "formal"
        
        # Adjust verbosity based on emotion and intensity
        if dominant_emotion in ["anger", "sadness"] and intensity > 0.7:
            adjustments["verbosity"] = "concise"  # Keep it brief when user is upset
        elif dominant_emotion == "joy":
            adjustments["verbosity"] = "elaborate"  # Can be more verbose when user is happy
        
        return adjustments