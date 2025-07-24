"""
Personalization adapter for CCAI chatbot.

This module provides functionality for personalizing responses based on
user profiles and preferences.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from ccai.user.profile import UserProfile, UserProfileManager

# Set up logging
logger = logging.getLogger(__name__)


class PersonalizationAdapter:
    """
    Adapts responses based on user profiles and preferences.
    
    This class is responsible for:
    - Adjusting response style based on user preferences
    - Incorporating user interests into responses
    - Maintaining consistent tone and formality
    """
    
    def __init__(self, profile_manager: UserProfileManager):
        """
        Initialize the personalization adapter.
        
        Args:
            profile_manager: The user profile manager
        """
        self.profile_manager = profile_manager
    
    def personalize_response(
        self,
        user_id: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Personalize a response for a specific user.
        
        Args:
            user_id: The user ID
            response: The original response
            context: Optional context information
            
        Returns:
            The personalized response
        """
        # Get the user profile
        profile = self.profile_manager.get_profile(user_id)
        
        # Apply personalizations
        personalized = response
        
        # Adjust response style
        personalized = self._adjust_response_style(personalized, profile)
        
        # Adjust formality
        personalized = self._adjust_formality(personalized, profile)
        
        # Add personal references
        personalized = self._add_personal_references(personalized, profile, context)
        
        # Adjust technical level
        personalized = self._adjust_technical_level(personalized, profile)
        
        # Add humor if appropriate
        personalized = self._add_humor(personalized, profile, context)
        
        return personalized
    
    def _adjust_response_style(self, response: str, profile: UserProfile) -> str:
        """Adjust the response style based on user preferences."""
        style = profile.get_preference("response_style", "balanced")
        
        if style == "concise":
            # Shorten the response
            sentences = response.split(". ")
            if len(sentences) > 3:
                # Keep first sentence, last sentence, and one in the middle
                middle_idx = len(sentences) // 2
                shortened = [sentences[0], sentences[middle_idx], sentences[-1]]
                return ". ".join(shortened) + "."
            return response
        
        elif style == "detailed":
            # For a real implementation, this would add more details
            # For now, we'll just add a note if the response is short
            if len(response.split()) < 30:
                return response + " I can provide more details if you'd like."
        
        # Default: balanced (return as is)
        return response
    
    def _adjust_formality(self, response: str, profile: UserProfile) -> str:
        """Adjust the formality level based on user preferences."""
        formality = profile.get_preference("formality_level", "neutral")
        
        if formality == "casual":
            # Make more casual
            casual_replacements = {
                r'\bI am\b': "I'm",
                r'\bYou are\b': "You're",
                r'\byou are\b': "you're",
                r'\bIt is\b': "It's",
                r'\bit is\b': "it's",
                r'\bDo not\b': "Don't",
                r'\bdo not\b': "don't",
                r'\bCannot\b': "Can't",
                r'\bcannot\b': "can't",
                r'\bWill not\b': "Won't",
                r'\bwill not\b': "won't",
            }
            
            result = response
            for pattern, replacement in casual_replacements.items():
                result = re.sub(pattern, replacement, result)
            
            return result
        
        elif formality == "formal":
            # Make more formal
            formal_replacements = {
                r'\bI\'m\b': "I am",
                r'\bYou\'re\b': "You are",
                r'\byou\'re\b': "you are",
                r'\bIt\'s\b': "It is",
                r'\bit\'s\b': "it is",
                r'\bDon\'t\b': "Do not",
                r'\bdon\'t\b': "do not",
                r'\bCan\'t\b': "Cannot",
                r'\bcan\'t\b': "cannot",
                r'\bWon\'t\b': "Will not",
                r'\bwon\'t\b': "will not",
            }
            
            result = response
            for pattern, replacement in formal_replacements.items():
                result = re.sub(pattern, replacement, result)
            
            return result
        
        # Default: neutral (return as is)
        return response
    
    def _add_personal_references(
        self,
        response: str,
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add personal references based on user history and preferences."""
        # Add name if available
        if profile.name and profile.name != profile.user_id:
            # Only add name if not already in the response
            if profile.name not in response:
                # 30% chance to add name at the beginning
                import random
                if random.random() < 0.3:
                    return f"{profile.name}, {response[0].lower()}{response[1:]}"
        
        # Reference top interests if relevant
        if context and "topic" in context:
            current_topic = context["topic"]
            top_topics = profile.get_top_topics()
            
            if current_topic in top_topics:
                # Add a reference to their interest in this topic
                if random.random() < 0.5:
                    return response + f" I know this is a topic you're interested in."
        
        return response
    
    def _adjust_technical_level(self, response: str, profile: UserProfile) -> str:
        """Adjust the technical level based on user preferences."""
        tech_level = profile.get_preference("technical_level", "medium")
        
        # This would be more sophisticated in a real implementation
        # For now, we'll just add a note for advanced users
        if tech_level == "advanced":
            # Check if the response is technical
            technical_terms = ["algorithm", "function", "parameter", "variable", "method", "class", "object"]
            has_technical = any(term in response.lower() for term in technical_terms)
            
            if has_technical:
                return response + " I've provided the technical details since I know you prefer that."
        
        return response
    
    def _add_humor(
        self,
        response: str,
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add humor based on user preferences."""
        humor_level = profile.get_preference("humor_level", "medium")
        
        if humor_level == "none":
            return response
        
        # Simple humor additions
        import random
        
        if humor_level == "light" and random.random() < 0.1:
            light_humor = [
                " 😊",
                " (with a smile)",
                " That's a bit interesting, isn't it?",
            ]
            return response + random.choice(light_humor)
        
        elif humor_level == "medium" and random.random() < 0.2:
            medium_humor = [
                " 😄",
                " Well, that's one way to look at it!",
                " I find that quite amusing, actually.",
                " Isn't that something?",
            ]
            return response + random.choice(medium_humor)
        
        elif humor_level == "high" and random.random() < 0.3:
            high_humor = [
                " 😂",
                " That's what she said! Just kidding.",
                " I'm not saying it's funny, but I'm definitely laughing.",
                " If I had a dollar for every time I've said that... I'd have exactly one dollar now.",
                " Plot twist: I actually have no idea what I'm talking about. (Just kidding!)",
            ]
            return response + random.choice(high_humor)
        
        return response


class EntityExtractor:
    """
    Extracts entities and topics from user messages.
    
    This class is responsible for:
    - Identifying entities mentioned in messages
    - Determining topics of conversation
    - Providing context for personalization
    """
    
    def __init__(self):
        """Initialize the entity extractor."""
        # This would use a proper NLP library in a real implementation
        # For now, we'll use simple pattern matching
        self.common_entities = [
            "car", "dog", "cat", "house", "computer", "phone", "book",
            "movie", "music", "food", "weather", "news", "sports",
            "politics", "science", "technology", "health", "education"
        ]
        
        self.topic_keywords = {
            "technology": ["computer", "phone", "software", "hardware", "app", "internet", "tech", "digital"],
            "science": ["physics", "chemistry", "biology", "research", "experiment", "theory", "scientific"],
            "entertainment": ["movie", "music", "book", "game", "play", "show", "concert", "theater"],
            "sports": ["football", "basketball", "soccer", "baseball", "game", "team", "player", "score"],
            "food": ["eat", "cook", "recipe", "restaurant", "meal", "dish", "taste", "flavor"],
            "travel": ["trip", "vacation", "visit", "country", "city", "hotel", "flight", "tour"],
            "health": ["doctor", "medicine", "exercise", "diet", "healthy", "illness", "symptom", "treatment"],
            "education": ["school", "learn", "study", "teacher", "student", "class", "course", "degree"]
        }
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text.
        
        Args:
            text: The text to extract entities from
            
        Returns:
            List of extracted entities
        """
        # This is a simplified implementation
        # In a real system, you would use a proper NER system
        entities = []
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in self.common_entities:
                entities.append(word)
        
        return entities
    
    def extract_topics(self, text: str) -> List[str]:
        """
        Extract topics from text.
        
        Args:
            text: The text to extract topics from
            
        Returns:
            List of extracted topics
        """
        # This is a simplified implementation
        # In a real system, you would use topic modeling
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics