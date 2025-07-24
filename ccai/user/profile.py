"""
User profile management for CCAI chatbot.

This module provides functionality for creating, updating, and retrieving
user profiles with preferences and interaction history.
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class UserProfile:
    """
    Represents a user profile with preferences and interaction history.
    
    This class stores:
    - Basic user information
    - User preferences
    - Interaction history
    - Topic interests
    - Response style preferences
    """
    
    def __init__(self, user_id: str, name: Optional[str] = None):
        """
        Initialize a user profile.
        
        Args:
            user_id: Unique identifier for the user
            name: Optional display name for the user
        """
        self.user_id = user_id
        self.name = name or user_id
        
        # Basic information
        self.created_at = time.time()
        self.last_active = time.time()
        self.session_count = 0
        
        # Preferences
        self.preferences = {
            "response_style": "balanced",  # balanced, concise, detailed
            "formality_level": "neutral",  # casual, neutral, formal
            "technical_level": "medium",   # basic, medium, advanced
            "humor_level": "medium",       # none, light, medium, high
            "language": "en",              # language code
        }
        
        # Interaction history
        self.interaction_stats = {
            "total_messages": 0,
            "questions_asked": 0,
            "commands_issued": 0,
            "statements_made": 0,
            "average_sentiment": 0.0,
        }
        
        # Topic interests (with scores from 0.0 to 1.0)
        self.topic_interests = {}
        
        # Frequently asked about entities
        self.frequent_entities = {}
        
        # Feedback history
        self.feedback_history = []
    
    def update_activity(self):
        """Update the last active timestamp."""
        self.last_active = time.time()
        self.session_count += 1
    
    def update_interaction_stats(self, message_type: str, sentiment_score: float):
        """
        Update interaction statistics.
        
        Args:
            message_type: Type of message (question, command, statement)
            sentiment_score: Sentiment score of the message
        """
        self.interaction_stats["total_messages"] += 1
        
        if message_type == "question":
            self.interaction_stats["questions_asked"] += 1
        elif message_type == "command":
            self.interaction_stats["commands_issued"] += 1
        elif message_type == "statement":
            self.interaction_stats["statements_made"] += 1
        
        # Update average sentiment
        total = self.interaction_stats["total_messages"]
        current_avg = self.interaction_stats["average_sentiment"]
        new_avg = ((current_avg * (total - 1)) + sentiment_score) / total
        self.interaction_stats["average_sentiment"] = new_avg
    
    def update_topic_interest(self, topic: str, interest_score: float = 0.1):
        """
        Update interest score for a topic.
        
        Args:
            topic: The topic to update
            interest_score: Amount to increase the interest score
        """
        current_score = self.topic_interests.get(topic, 0.0)
        new_score = min(1.0, current_score + interest_score)
        self.topic_interests[topic] = new_score
    
    def update_entity_frequency(self, entity: str):
        """
        Update frequency count for an entity.
        
        Args:
            entity: The entity to update
        """
        self.frequent_entities[entity] = self.frequent_entities.get(entity, 0) + 1
    
    def add_feedback(self, response_id: str, rating: int, comments: Optional[str] = None):
        """
        Add feedback for a response.
        
        Args:
            response_id: ID of the response
            rating: Rating (1-5)
            comments: Optional comments
        """
        self.feedback_history.append({
            "response_id": response_id,
            "rating": rating,
            "comments": comments,
            "timestamp": time.time()
        })
    
    def set_preference(self, preference: str, value: Any):
        """
        Set a user preference.
        
        Args:
            preference: The preference to set
            value: The value to set
        """
        if preference in self.preferences:
            self.preferences[preference] = value
    
    def get_preference(self, preference: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            preference: The preference to get
            default: Default value if preference doesn't exist
            
        Returns:
            The preference value or default
        """
        return self.preferences.get(preference, default)
    
    def get_top_topics(self, limit: int = 5) -> List[str]:
        """
        Get the user's top topics of interest.
        
        Args:
            limit: Maximum number of topics to return
            
        Returns:
            List of top topics
        """
        sorted_topics = sorted(
            self.topic_interests.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [topic for topic, _ in sorted_topics[:limit]]
    
    def get_top_entities(self, limit: int = 5) -> List[str]:
        """
        Get the user's most frequently mentioned entities.
        
        Args:
            limit: Maximum number of entities to return
            
        Returns:
            List of top entities
        """
        sorted_entities = sorted(
            self.frequent_entities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [entity for entity, _ in sorted_entities[:limit]]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary.
        
        Returns:
            Dictionary representation of the profile
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "session_count": self.session_count,
            "preferences": self.preferences,
            "interaction_stats": self.interaction_stats,
            "topic_interests": self.topic_interests,
            "frequent_entities": self.frequent_entities,
            "feedback_history": self.feedback_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """
        Create a profile from a dictionary.
        
        Args:
            data: Dictionary representation of a profile
            
        Returns:
            UserProfile object
        """
        profile = cls(user_id=data["user_id"], name=data["name"])
        profile.created_at = data["created_at"]
        profile.last_active = data["last_active"]
        profile.session_count = data["session_count"]
        profile.preferences = data["preferences"]
        profile.interaction_stats = data["interaction_stats"]
        profile.topic_interests = data["topic_interests"]
        profile.frequent_entities = data["frequent_entities"]
        profile.feedback_history = data["feedback_history"]
        return profile


class UserProfileManager:
    """
    Manages user profiles, including storage and retrieval.
    
    This class is responsible for:
    - Creating and retrieving user profiles
    - Persisting profiles to disk
    - Providing personalization suggestions
    """
    
    def __init__(self, storage_dir: Path):
        """
        Initialize the profile manager.
        
        Args:
            storage_dir: Directory to store user profiles
        """
        self.storage_dir = storage_dir
        self.profiles_dir = storage_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache of loaded profiles
        self.profile_cache: Dict[str, UserProfile] = {}
    
    def get_profile(self, user_id: str) -> UserProfile:
        """
        Get a user profile, creating it if it doesn't exist.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user profile
        """
        # Check cache first
        if user_id in self.profile_cache:
            return self.profile_cache[user_id]
        
        # Try to load from disk
        profile_path = self.profiles_dir / f"{user_id}.json"
        if profile_path.exists():
            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)
                profile = UserProfile.from_dict(data)
                self.profile_cache[user_id] = profile
                return profile
            except Exception as e:
                logger.error(f"Error loading profile for {user_id}: {e}")
        
        # Create new profile
        profile = UserProfile(user_id)
        self.profile_cache[user_id] = profile
        self.save_profile(profile)
        return profile
    
    def save_profile(self, profile: UserProfile) -> bool:
        """
        Save a user profile to disk.
        
        Args:
            profile: The profile to save
            
        Returns:
            True if successful, False otherwise
        """
        profile_path = self.profiles_dir / f"{profile.user_id}.json"
        try:
            with open(profile_path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving profile for {profile.user_id}: {e}")
            return False
    
    def update_profile(
        self,
        user_id: str,
        message: str,
        message_type: str,
        sentiment_score: float,
        entities: List[str],
        topics: List[str]
    ):
        """
        Update a user profile based on a message.
        
        Args:
            user_id: The user ID
            message: The user's message
            message_type: Type of message (question, command, statement)
            sentiment_score: Sentiment score of the message
            entities: Entities mentioned in the message
            topics: Topics mentioned in the message
        """
        profile = self.get_profile(user_id)
        
        # Update activity
        profile.update_activity()
        
        # Update interaction stats
        profile.update_interaction_stats(message_type, sentiment_score)
        
        # Update entities
        for entity in entities:
            profile.update_entity_frequency(entity)
        
        # Update topics
        for topic in topics:
            profile.update_topic_interest(topic)
        
        # Save the updated profile
        self.save_profile(profile)
    
    def get_personalization_suggestions(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalization suggestions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary of personalization suggestions
        """
        profile = self.get_profile(user_id)
        
        suggestions = {
            "response_style": profile.get_preference("response_style"),
            "formality_level": profile.get_preference("formality_level"),
            "technical_level": profile.get_preference("technical_level"),
            "humor_level": profile.get_preference("humor_level"),
            "language": profile.get_preference("language"),
            "top_topics": profile.get_top_topics(),
            "top_entities": profile.get_top_entities(),
            "sentiment_baseline": profile.interaction_stats.get("average_sentiment", 0.0)
        }
        
        return suggestions
    
    def list_all_profiles(self) -> List[str]:
        """
        List all user IDs with profiles.
        
        Returns:
            List of user IDs
        """
        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            profiles.append(file.stem)
        return profiles