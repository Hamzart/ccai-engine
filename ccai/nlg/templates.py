"""
Template-based response generation for CCAI chatbot.

This module provides functionality for selecting and filling templates
to generate natural language responses.
"""

import random
from typing import Dict, List, Any, Optional
from string import Template


class TemplateEngine:
    """
    Manages templates for generating natural language responses.
    
    The TemplateEngine is responsible for:
    - Storing templates for different response types
    - Selecting appropriate templates based on context
    - Filling templates with data from reasoning results
    """
    
    def __init__(self):
        """Initialize the template engine with default templates."""
        # Templates for different types of responses
        self.templates: Dict[str, List[str]] = {
            # Templates for definition questions (What is X?)
            "definition": [
                "$entity is a $category.",
                "$entity is defined as a $category.",
                "A $entity is a type of $category.",
                "In my knowledge, $entity is a $category."
            ],
            
            # Templates for property questions (What color is X?)
            "property": [
                "The $property of $entity is $value.",
                "$entity has a $property of $value.",
                "The $entity is $value in terms of $property."
            ],
            
            # Templates for capability questions (Can X do Y?)
            "capability": [
                "Yes, $entity can $action.",
                "$entity is capable of $action.",
                "Based on my knowledge, $entity can $action."
            ],
            
            # Templates for negative capability responses
            "capability_negative": [
                "No, $entity cannot $action.",
                "I don't have information that $entity can $action.",
                "Based on my knowledge, $entity is not capable of $action."
            ],
            
            # Templates for part questions (What parts does X have?)
            "part": [
                "$entity has $parts.",
                "The parts of $entity include $parts.",
                "$entity consists of $parts."
            ],
            
            # Templates for purpose questions (What is X used for?)
            "purpose": [
                "$entity is used for $purposes.",
                "The purpose of $entity is $purposes.",
                "$entity is typically used for $purposes."
            ],
            
            # Templates for learning acknowledgments
            "learning": [
                "I've learned that $fact. Thank you for teaching me.",
                "Thank you for telling me that $fact. I've added this to my knowledge.",
                "I've added to my knowledge that $fact. This helps me learn."
            ],
            
            # Templates for unknown concepts
            "unknown_concept": [
                "I don't have any information about $entity in my knowledge base.",
                "I'm not familiar with $entity based on my current knowledge.",
                "$entity is not in my knowledge base yet."
            ],
            
            # Templates for uncertain responses
            "uncertain": [
                "I'm not entirely sure, but I think $answer.",
                "Based on limited information, $answer.",
                "I'm uncertain, but possibly $answer."
            ],
            
            # Templates for fallback responses
            "fallback": [
                "I don't know how to answer that question.",
                "I don't have enough information to provide an answer.",
                "I'm still learning and don't know the answer to that yet according to my knowledge base."
            ]
        }
    
    def add_template(self, category: str, template: str) -> None:
        """
        Add a new template to a category.
        
        Args:
            category: The category to add the template to
            template: The template string to add
        """
        if category not in self.templates:
            self.templates[category] = []
        self.templates[category].append(template)
    
    def select_template(self, category: str) -> str:
        """
        Select a random template from the specified category.
        
        Args:
            category: The category to select a template from
            
        Returns:
            A template string from the category
        """
        if category not in self.templates or not self.templates[category]:
            # Fallback to a generic template if the category doesn't exist
            return "I know that $answer."
        
        return random.choice(self.templates[category])
    
    def fill_template(self, template_str: str, data: Dict[str, Any]) -> str:
        """
        Fill a template with data.
        
        Args:
            template_str: The template string to fill
            data: Dictionary of values to substitute into the template
            
        Returns:
            The filled template string
        """
        template = Template(template_str)
        try:
            return template.substitute(data)
        except KeyError as e:
            # If a key is missing, try safe_substitute which doesn't raise an error
            return template.safe_substitute(data)


class VariationGenerator:
    """
    Adds variations to responses to make them more natural and diverse.
    
    The VariationGenerator is responsible for:
    - Adding filler words and phrases
    - Varying sentence structures
    - Adding appropriate prefixes and suffixes to responses
    """
    
    def __init__(self):
        """Initialize the variation generator with common variations."""
        # Prefixes to occasionally add to responses
        self.prefixes = [
            "I believe ",
            "As far as I know, ",
            "Based on my knowledge, ",
            "From what I understand, ",
            "According to my information, "
        ]
        
        # Suffixes to occasionally add to responses
        self.suffixes = [
            " if I'm not mistaken.",
            " based on what I've learned.",
            " according to my knowledge base.",
            ".",
            "!"
        ]
        
        # Filler words to occasionally insert
        self.fillers = [
            "actually",
            "basically",
            "essentially",
            "generally",
            "primarily"
        ]
        
        # Probability of adding variations
        self.prefix_prob = 0.3
        self.suffix_prob = 0.2
        self.filler_prob = 0.1
    
    def apply_variations(self, text: str) -> str:
        """
        Apply random variations to the text to make it more natural.
        
        Args:
            text: The original text
            
        Returns:
            The text with variations applied
        """
        # Maybe add a prefix
        if random.random() < self.prefix_prob:
            text = random.choice(self.prefixes) + text
        
        # Maybe add a suffix
        if random.random() < self.suffix_prob:
            # Remove trailing period if present
            if text.endswith("."):
                text = text[:-1]
            text = text + random.choice(self.suffixes)
        
        # Maybe add a filler word (more complex and not implemented here)
        # This would require parsing the sentence structure
        
        return text