"""
Integration module for connecting the Conversation Manager with the Knowledge Graph.

This module provides classes and functions for integrating the Conversation Manager
with the Knowledge Graph, enabling knowledge-based conversations.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import re
from datetime import datetime

from ..conversation.conversation_context import ConversationContext, Message, MessageType
from ..conversation.intent_recognizer import Intent, IntentType
from ..knowledge.knowledge_graph import KnowledgeGraph
from ..knowledge.concept_node import ConceptNode
from ..knowledge.relation import Relation
from ..knowledge.property_value import PropertyValue


class ConversationKnowledgeIntegration:
    """
    Integrates the Conversation Manager with the Knowledge Graph.
    
    This class provides methods for querying the Knowledge Graph based on user intents,
    updating the Knowledge Graph based on user interactions, and extracting knowledge
    from user messages.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance to integrate with.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the ConversationKnowledgeIntegration.
        
        Args:
            knowledge_graph: The KnowledgeGraph instance to integrate with.
        """
        self.knowledge_graph = knowledge_graph
    
    def query_knowledge_graph(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Query the Knowledge Graph based on a user intent.
        
        Args:
            intent: The user intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        if intent.type == IntentType.QUESTION:
            return self._handle_question_intent(intent, context)
        elif intent.type == IntentType.DEFINITION:
            return self._handle_definition_intent(intent, context)
        elif intent.type == IntentType.VERIFICATION:
            return self._handle_verification_intent(intent, context)
        elif intent.type == IntentType.RELATIONSHIP:
            return self._handle_relationship_intent(intent, context)
        elif intent.type == IntentType.PROPERTY:
            return self._handle_property_intent(intent, context)
        else:
            return {"success": False, "error": "Unsupported intent type for knowledge graph query"}
    
    def _handle_question_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a question intent.
        
        Args:
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Extract the topic from the intent
        topic = intent.entities.get("topic")
        if not topic:
            return {"success": False, "error": "No topic specified in the question"}
        
        # Get the concept node for the topic
        concept = self.knowledge_graph.get_concept_by_name(topic)
        if not concept:
            return {"success": False, "error": f"No knowledge found about '{topic}'"}
        
        # Extract the question type
        question_type = intent.metadata.get("question_type", "general")
        
        if question_type == "what_is":
            # Handle "what is" questions
            return self._handle_what_is_question(concept, intent, context)
        elif question_type == "how_to":
            # Handle "how to" questions
            return self._handle_how_to_question(concept, intent, context)
        elif question_type == "why":
            # Handle "why" questions
            return self._handle_why_question(concept, intent, context)
        elif question_type == "when":
            # Handle "when" questions
            return self._handle_when_question(concept, intent, context)
        elif question_type == "where":
            # Handle "where" questions
            return self._handle_where_question(concept, intent, context)
        elif question_type == "who":
            # Handle "who" questions
            return self._handle_who_question(concept, intent, context)
        else:
            # Handle general questions
            return self._handle_general_question(concept, intent, context)
    
    def _handle_what_is_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "what is" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the definition of the concept
        definition = concept.get_property("definition")
        if definition:
            return {
                "success": True,
                "type": "definition",
                "concept": concept.name,
                "definition": definition.value
            }
        
        # If there's no explicit definition, generate one from properties
        properties = concept.get_all_properties()
        if properties:
            definition = f"{concept.name} is "
            
            # Get the "is_a" relations
            is_a_relations = self.knowledge_graph.get_relations(concept, "is_a")
            if is_a_relations:
                is_a_concepts = [rel.target.name for rel in is_a_relations]
                if len(is_a_concepts) == 1:
                    definition += f"a {is_a_concepts[0]}"
                else:
                    definition += "a " + ", ".join(is_a_concepts[:-1]) + f" and {is_a_concepts[-1]}"
                definition += " that "
            
            # Add properties
            property_strings = []
            for prop_name, prop_value in properties.items():
                if prop_name != "definition" and prop_name != "name":
                    property_strings.append(f"{prop_name} {prop_value.value}")
            
            if property_strings:
                if len(property_strings) == 1:
                    definition += property_strings[0]
                else:
                    definition += ", ".join(property_strings[:-1]) + f" and {property_strings[-1]}"
            
            return {
                "success": True,
                "type": "generated_definition",
                "concept": concept.name,
                "definition": definition
            }
        
        # If there are no properties, return a simple response
        return {
            "success": True,
            "type": "simple_definition",
            "concept": concept.name,
            "definition": f"{concept.name} is a concept in the knowledge graph."
        }
    
    def _handle_how_to_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "how to" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the "how_to" property of the concept
        how_to = concept.get_property("how_to")
        if how_to:
            return {
                "success": True,
                "type": "how_to",
                "concept": concept.name,
                "how_to": how_to.value
            }
        
        # If there's no "how_to" property, check for "steps" or "procedure"
        steps = concept.get_property("steps") or concept.get_property("procedure")
        if steps:
            return {
                "success": True,
                "type": "steps",
                "concept": concept.name,
                "steps": steps.value
            }
        
        # If there are no relevant properties, return a failure
        return {
            "success": False,
            "error": f"No information found on how to {concept.name}"
        }
    
    def _handle_why_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "why" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the "reason" or "explanation" property of the concept
        reason = concept.get_property("reason") or concept.get_property("explanation")
        if reason:
            return {
                "success": True,
                "type": "reason",
                "concept": concept.name,
                "reason": reason.value
            }
        
        # If there's no relevant property, return a failure
        return {
            "success": False,
            "error": f"No information found on why {concept.name}"
        }
    
    def _handle_when_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "when" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the "time", "date", or "period" property of the concept
        time_prop = concept.get_property("time") or concept.get_property("date") or concept.get_property("period")
        if time_prop:
            return {
                "success": True,
                "type": "time",
                "concept": concept.name,
                "time": time_prop.value
            }
        
        # If there's no relevant property, return a failure
        return {
            "success": False,
            "error": f"No information found on when {concept.name}"
        }
    
    def _handle_where_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "where" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the "location" or "place" property of the concept
        location = concept.get_property("location") or concept.get_property("place")
        if location:
            return {
                "success": True,
                "type": "location",
                "concept": concept.name,
                "location": location.value
            }
        
        # If there's no relevant property, return a failure
        return {
            "success": False,
            "error": f"No information found on where {concept.name}"
        }
    
    def _handle_who_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a "who" question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the "person" or "creator" property of the concept
        person = concept.get_property("person") or concept.get_property("creator")
        if person:
            return {
                "success": True,
                "type": "person",
                "concept": concept.name,
                "person": person.value
            }
        
        # If there's no relevant property, return a failure
        return {
            "success": False,
            "error": f"No information found on who {concept.name}"
        }
    
    def _handle_general_question(self, concept: ConceptNode, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a general question.
        
        Args:
            concept: The concept node for the topic.
            intent: The question intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get all properties of the concept
        properties = concept.get_all_properties()
        
        # Get all relations of the concept
        relations = self.knowledge_graph.get_all_relations(concept)
        
        return {
            "success": True,
            "type": "general",
            "concept": concept.name,
            "properties": {name: prop.value for name, prop in properties.items()},
            "relations": [
                {
                    "type": rel.type,
                    "target": rel.target.name,
                    "bidirectional": rel.bidirectional
                }
                for rel in relations
            ]
        }
    
    def _handle_definition_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a definition intent.
        
        Args:
            intent: The definition intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Extract the term from the intent
        term = intent.entities.get("term")
        if not term:
            return {"success": False, "error": "No term specified for definition"}
        
        # Get the concept node for the term
        concept = self.knowledge_graph.get_concept_by_name(term)
        if not concept:
            return {"success": False, "error": f"No definition found for '{term}'"}
        
        # Get the definition of the concept
        definition = concept.get_property("definition")
        if definition:
            return {
                "success": True,
                "type": "definition",
                "term": term,
                "definition": definition.value
            }
        
        # If there's no explicit definition, generate one from properties
        return self._handle_what_is_question(concept, intent, context)
    
    def _handle_verification_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a verification intent.
        
        Args:
            intent: The verification intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Extract the subject and object from the intent
        subject = intent.entities.get("subject")
        object_ = intent.entities.get("object")
        
        if not subject or not object_:
            return {"success": False, "error": "Missing subject or object for verification"}
        
        # Get the concept nodes for the subject and object
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        object_concept = self.knowledge_graph.get_concept_by_name(object_)
        
        if not subject_concept:
            return {"success": False, "error": f"No knowledge found about '{subject}'"}
        
        if not object_concept:
            return {"success": False, "error": f"No knowledge found about '{object_}'"}
        
        # Check if there's an "is_a" relation between the subject and object
        is_a_relation = self.knowledge_graph.get_relation(subject_concept, object_concept, "is_a")
        
        if is_a_relation:
            return {
                "success": True,
                "type": "verification",
                "subject": subject,
                "object": object_,
                "relation": "is_a",
                "verified": True,
                "confidence": is_a_relation.confidence
            }
        
        # Check if there's any relation between the subject and object
        relation = self.knowledge_graph.get_relation(subject_concept, object_concept)
        
        if relation:
            return {
                "success": True,
                "type": "verification",
                "subject": subject,
                "object": object_,
                "relation": relation.type,
                "verified": True,
                "confidence": relation.confidence
            }
        
        # If there's no relation, check if the object is a property of the subject
        property_value = subject_concept.get_property(object_)
        
        if property_value:
            return {
                "success": True,
                "type": "property_verification",
                "subject": subject,
                "property": object_,
                "value": property_value.value,
                "verified": True,
                "confidence": property_value.confidence
            }
        
        # If there's no relation or property, the verification fails
        return {
            "success": True,
            "type": "verification",
            "subject": subject,
            "object": object_,
            "verified": False,
            "confidence": 0.0
        }
    
    def _handle_relationship_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a relationship intent.
        
        Args:
            intent: The relationship intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Extract the subject, object, and relation type from the intent
        subject = intent.entities.get("subject")
        object_ = intent.entities.get("object")
        relation_type = intent.entities.get("relation_type")
        
        if not subject:
            return {"success": False, "error": "No subject specified for relationship query"}
        
        # Get the concept node for the subject
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            return {"success": False, "error": f"No knowledge found about '{subject}'"}
        
        if object_:
            # If an object is specified, get the concept node for the object
            object_concept = self.knowledge_graph.get_concept_by_name(object_)
            if not object_concept:
                return {"success": False, "error": f"No knowledge found about '{object_}'"}
            
            # Check if there's a relation between the subject and object
            if relation_type:
                # If a relation type is specified, check for that specific relation
                relation = self.knowledge_graph.get_relation(subject_concept, object_concept, relation_type)
                
                if relation:
                    return {
                        "success": True,
                        "type": "specific_relation",
                        "subject": subject,
                        "object": object_,
                        "relation_type": relation_type,
                        "exists": True,
                        "confidence": relation.confidence
                    }
                else:
                    return {
                        "success": True,
                        "type": "specific_relation",
                        "subject": subject,
                        "object": object_,
                        "relation_type": relation_type,
                        "exists": False,
                        "confidence": 0.0
                    }
            else:
                # If no relation type is specified, check for any relation
                relation = self.knowledge_graph.get_relation(subject_concept, object_concept)
                
                if relation:
                    return {
                        "success": True,
                        "type": "any_relation",
                        "subject": subject,
                        "object": object_,
                        "relation_type": relation.type,
                        "exists": True,
                        "confidence": relation.confidence
                    }
                else:
                    return {
                        "success": True,
                        "type": "any_relation",
                        "subject": subject,
                        "object": object_,
                        "exists": False,
                        "confidence": 0.0
                    }
        elif relation_type:
            # If only a relation type is specified, get all relations of that type
            relations = self.knowledge_graph.get_relations(subject_concept, relation_type)
            
            if relations:
                return {
                    "success": True,
                    "type": "relations_by_type",
                    "subject": subject,
                    "relation_type": relation_type,
                    "relations": [
                        {
                            "target": rel.target.name,
                            "confidence": rel.confidence
                        }
                        for rel in relations
                    ]
                }
            else:
                return {
                    "success": True,
                    "type": "relations_by_type",
                    "subject": subject,
                    "relation_type": relation_type,
                    "relations": []
                }
        else:
            # If neither object nor relation type is specified, get all relations
            relations = self.knowledge_graph.get_all_relations(subject_concept)
            
            if relations:
                return {
                    "success": True,
                    "type": "all_relations",
                    "subject": subject,
                    "relations": [
                        {
                            "type": rel.type,
                            "target": rel.target.name,
                            "confidence": rel.confidence
                        }
                        for rel in relations
                    ]
                }
            else:
                return {
                    "success": True,
                    "type": "all_relations",
                    "subject": subject,
                    "relations": []
                }
    
    def _handle_property_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a property intent.
        
        Args:
            intent: The property intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the query results.
        """
        # Extract the subject and property from the intent
        subject = intent.entities.get("subject")
        property_ = intent.entities.get("property")
        
        if not subject:
            return {"success": False, "error": "No subject specified for property query"}
        
        # Get the concept node for the subject
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            return {"success": False, "error": f"No knowledge found about '{subject}'"}
        
        if property_:
            # If a property is specified, get that specific property
            property_value = subject_concept.get_property(property_)
            
            if property_value:
                return {
                    "success": True,
                    "type": "specific_property",
                    "subject": subject,
                    "property": property_,
                    "value": property_value.value,
                    "confidence": property_value.confidence
                }
            else:
                return {
                    "success": True,
                    "type": "specific_property",
                    "subject": subject,
                    "property": property_,
                    "exists": False,
                    "confidence": 0.0
                }
        else:
            # If no property is specified, get all properties
            properties = subject_concept.get_all_properties()
            
            if properties:
                return {
                    "success": True,
                    "type": "all_properties",
                    "subject": subject,
                    "properties": {
                        name: {
                            "value": prop.value,
                            "confidence": prop.confidence
                        }
                        for name, prop in properties.items()
                    }
                }
            else:
                return {
                    "success": True,
                    "type": "all_properties",
                    "subject": subject,
                    "properties": {}
                }
    
    def update_knowledge_graph(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Update the Knowledge Graph based on a user intent.
        
        Args:
            intent: The user intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the update results.
        """
        if intent.type == IntentType.STATEMENT:
            return self._handle_statement_intent(intent, context)
        elif intent.type == IntentType.CORRECTION:
            return self._handle_correction_intent(intent, context)
        else:
            return {"success": False, "error": "Unsupported intent type for knowledge graph update"}
    
    def _handle_statement_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a statement intent.
        
        Args:
            intent: The statement intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the update results.
        """
        # Extract the subject, predicate, and object from the intent
        subject = intent.entities.get("subject")
        predicate = intent.entities.get("predicate")
        object_ = intent.entities.get("object")
        
        if not subject:
            return {"success": False, "error": "No subject specified in the statement"}
        
        # Get or create the concept node for the subject
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            subject_concept = self.knowledge_graph.add_concept(subject)
        
        if predicate == "is" or predicate == "are":
            # Handle "is" or "are" statements
            if not object_:
                return {"success": False, "error": "No object specified in the statement"}
            
            # Check if the object is a property value
            if "=" in object_:
                # Handle property assignment
                property_name, property_value = object_.split("=", 1)
                property_name = property_name.strip()
                property_value = property_value.strip()
                
                # Set the property
                subject_concept.set_property(property_name, property_value)
                
                return {
                    "success": True,
                    "type": "property_assignment",
                    "subject": subject,
                    "property": property_name,
                    "value": property_value
                }
            else:
                # Handle "is_a" relation
                # Get or create the concept node for the object
                object_concept = self.knowledge_graph.get_concept_by_name(object_)
                if not object_concept:
                    object_concept = self.knowledge_graph.add_concept(object_)
                
                # Create an "is_a" relation
                self.knowledge_graph.update_relation(subject_concept, object_concept, "is_a")
                
                return {
                    "success": True,
                    "type": "is_a_relation",
                    "subject": subject,
                    "object": object_
                }
        elif predicate == "has" or predicate == "have":
            # Handle "has" or "have" statements
            if not object_:
                return {"success": False, "error": "No object specified in the statement"}
            
            # Check if the object is a property value
            if "=" in object_:
                # Handle property assignment
                property_name, property_value = object_.split("=", 1)
                property_name = property_name.strip()
                property_value = property_value.strip()
                
                # Set the property
                subject_concept.set_property(property_name, property_value)
                
                return {
                    "success": True,
                    "type": "property_assignment",
                    "subject": subject,
                    "property": property_name,
                    "value": property_value
                }
            else:
                # Handle "has" relation
                # Get or create the concept node for the object
                object_concept = self.knowledge_graph.get_concept_by_name(object_)
                if not object_concept:
                    object_concept = self.knowledge_graph.add_concept(object_)
                
                # Create a "has" relation
                self.knowledge_graph.update_relation(subject_concept, object_concept, "has")
                
                return {
                    "success": True,
                    "type": "has_relation",
                    "subject": subject,
                    "object": object_
                }
        else:
            # Handle other predicates
            if not object_:
                return {"success": False, "error": "No object specified in the statement"}
            
            # Get or create the concept node for the object
            object_concept = self.knowledge_graph.get_concept_by_name(object_)
            if not object_concept:
                object_concept = self.knowledge_graph.add_concept(object_)
            
            # Create a relation with the predicate as the relation type
            self.knowledge_graph.update_relation(subject_concept, object_concept, predicate)
            
            return {
                "success": True,
                "type": "custom_relation",
                "subject": subject,
                "predicate": predicate,
                "object": object_
            }
    
    def _handle_correction_intent(self, intent: Intent, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a correction intent.
        
        Args:
            intent: The correction intent.
            context: The conversation context.
            
        Returns:
            A dictionary containing the update results.
        """
        # Extract the subject, predicate, old_object, and new_object from the intent
        subject = intent.entities.get("subject")
        predicate = intent.entities.get("predicate")
        old_object = intent.entities.get("old_object")
        new_object = intent.entities.get("new_object")
        
        if not subject:
            return {"success": False, "error": "No subject specified in the correction"}
        
        if not predicate:
            return {"success": False, "error": "No predicate specified in the correction"}
        
        if not old_object:
            return {"success": False, "error": "No old object specified in the correction"}
        
        if not new_object:
            return {"success": False, "error": "No new object specified in the correction"}
        
        # Get the concept node for the subject
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            return {"success": False, "error": f"No knowledge found about '{subject}'"}
        
        if predicate == "is" or predicate == "are":
            # Handle "is" or "are" corrections
            if "=" in old_object and "=" in new_object:
                # Handle property correction
                old_property_name, old_property_value = old_object.split("=", 1)
                new_property_name, new_property_value = new_object.split("=", 1)
                
                old_property_name = old_property_name.strip()
                old_property_value = old_property_value.strip()
                new_property_name = new_property_name.strip()
                new_property_value = new_property_value.strip()
                
                # Check if the old property exists
                old_property = subject_concept.get_property(old_property_name)
                if not old_property or old_property.value != old_property_value:
                    return {
                        "success": False,
                        "error": f"Property '{old_property_name}' with value '{old_property_value}' not found for '{subject}'"
                    }
                
                # Remove the old property
                subject_concept.remove_property(old_property_name)
                
                # Set the new property
                subject_concept.set_property(new_property_name, new_property_value)
                
                return {
                    "success": True,
                    "type": "property_correction",
                    "subject": subject,
                    "old_property": old_property_name,
                    "old_value": old_property_value,
                    "new_property": new_property_name,
                    "new_value": new_property_value
                }
            else:
                # Handle "is_a" relation correction
                # Get the concept nodes for the old and new objects
                old_object_concept = self.knowledge_graph.get_concept_by_name(old_object)
                if not old_object_concept:
                    return {"success": False, "error": f"No knowledge found about '{old_object}'"}
                
                # Check if the old relation exists
                old_relation = self.knowledge_graph.get_relation(subject_concept, old_object_concept, "is_a")
                if not old_relation:
                    return {
                        "success": False,
                        "error": f"Relation '{subject} is_a {old_object}' not found"
                    }
                
                # Get or create the concept node for the new object
                new_object_concept = self.knowledge_graph.get_concept_by_name(new_object)
                if not new_object_concept:
                    new_object_concept = self.knowledge_graph.add_concept(new_object)
                
                # Remove the old relation
                self.knowledge_graph.remove_relation(subject_concept, old_object_concept, "is_a")
                
                # Create the new relation
                self.knowledge_graph.update_relation(subject_concept, new_object_concept, "is_a")
                
                return {
                    "success": True,
                    "type": "is_a_relation_correction",
                    "subject": subject,
                    "old_object": old_object,
                    "new_object": new_object
                }
        elif predicate == "has" or predicate == "have":
            # Handle "has" or "have" corrections
            if "=" in old_object and "=" in new_object:
                # Handle property correction
                old_property_name, old_property_value = old_object.split("=", 1)
                new_property_name, new_property_value = new_object.split("=", 1)
                
                old_property_name = old_property_name.strip()
                old_property_value = old_property_value.strip()
                new_property_name = new_property_name.strip()
                new_property_value = new_property_value.strip()
                
                # Check if the old property exists
                old_property = subject_concept.get_property(old_property_name)
                if not old_property or old_property.value != old_property_value:
                    return {
                        "success": False,
                        "error": f"Property '{old_property_name}' with value '{old_property_value}' not found for '{subject}'"
                    }
                
                # Remove the old property
                subject_concept.remove_property(old_property_name)
                
                # Set the new property
                subject_concept.set_property(new_property_name, new_property_value)
                
                return {
                    "success": True,
                    "type": "property_correction",
                    "subject": subject,
                    "old_property": old_property_name,
                    "old_value": old_property_value,
                    "new_property": new_property_name,
                    "new_value": new_property_value
                }
            else:
                # Handle "has" relation correction
                # Get the concept nodes for the old and new objects
                old_object_concept = self.knowledge_graph.get_concept_by_name(old_object)
                if not old_object_concept:
                    return {"success": False, "error": f"No knowledge found about '{old_object}'"}
                
                # Check if the old relation exists
                old_relation = self.knowledge_graph.get_relation(subject_concept, old_object_concept, "has")
                if not old_relation:
                    return {
                        "success": False,
                        "error": f"Relation '{subject} has {old_object}' not found"
                    }
                
                # Get or create the concept node for the new object
                new_object_concept = self.knowledge_graph.get_concept_by_name(new_object)
                if not new_object_concept:
                    new_object_concept = self.knowledge_graph.add_concept(new_object)
                
                # Remove the old relation
                self.knowledge_graph.remove_relation(subject_concept, old_object_concept, "has")
                
                # Create the new relation
                self.knowledge_graph.update_relation(subject_concept, new_object_concept, "has")
                
                return {
                    "success": True,
                    "type": "has_relation_correction",
                    "subject": subject,
                    "old_object": old_object,
                    "new_object": new_object
                }
        else:
            # Handle other predicate corrections
            # Get the concept nodes for the old and new objects
            old_object_concept = self.knowledge_graph.get_concept_by_name(old_object)
            if not old_object_concept:
                return {"success": False, "error": f"No knowledge found about '{old_object}'"}
            
            # Check if the old relation exists
            old_relation = self.knowledge_graph.get_relation(subject_concept, old_object_concept, predicate)
            if not old_relation:
                return {
                    "success": False,
                    "error": f"Relation '{subject} {predicate} {old_object}' not found"
                }
            
            # Get or create the concept node for the new object
            new_object_concept = self.knowledge_graph.get_concept_by_name(new_object)
            if not new_object_concept:
                new_object_concept = self.knowledge_graph.add_concept(new_object)
            
            # Remove the old relation
            self.knowledge_graph.remove_relation(subject_concept, old_object_concept, predicate)
            
            # Create the new relation
            self.knowledge_graph.update_relation(subject_concept, new_object_concept, predicate)
            
            return {
                "success": True,
                "type": "custom_relation_correction",
                "subject": subject,
                "predicate": predicate,
                "old_object": old_object,
                "new_object": new_object
            }
    
    def extract_knowledge(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """
        Extract knowledge from a user message.
        
        Args:
            message: The user message.
            context: The conversation context.
            
        Returns:
            A dictionary containing the extracted knowledge.
        """
        # Extract statements from the message
        statements = self._extract_statements(message)
        
        # Extract definitions from the message
        definitions = self._extract_definitions(message)
        
        # Extract relationships from the message
        relationships = self._extract_relationships(message)
        
        # Extract properties from the message
        properties = self._extract_properties(message)
        
        # Process the extracted knowledge
        results = {
            "statements": [],
            "definitions": [],
            "relationships": [],
            "properties": []
        }
        
        # Process statements
        for statement in statements:
            result = self._process_statement(statement)
            if result["success"]:
                results["statements"].append(result)
        
        # Process definitions
        for definition in definitions:
            result = self._process_definition(definition)
            if result["success"]:
                results["definitions"].append(result)
        
        # Process relationships
        for relationship in relationships:
            result = self._process_relationship(relationship)
            if result["success"]:
                results["relationships"].append(result)
        
        # Process properties
        for property_ in properties:
            result = self._process_property(property_)
            if result["success"]:
                results["properties"].append(result)
        
        return results
    
    def _extract_statements(self, message: str) -> List[Dict[str, str]]:
        """
        Extract statements from a message.
        
        Args:
            message: The message to extract statements from.
            
        Returns:
            A list of dictionaries, where each dictionary contains the subject,
            predicate, and object of a statement.
        """
        statements = []
        
        # Define patterns for extracting statements
        patterns = [
            # "X is Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X are Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+are\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X has Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+has\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X have Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+have\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X [predicate] Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+(?P<predicate>\w+)\s+(?P<object>\w+(?:\s+\w+)*)"
        ]
        
        # Extract statements using the patterns
        for pattern in patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                statement = match.groupdict()
                if "predicate" not in statement:
                    if "is" in match.group():
                        statement["predicate"] = "is"
                    elif "are" in match.group():
                        statement["predicate"] = "are"
                    elif "has" in match.group():
                        statement["predicate"] = "has"
                    elif "have" in match.group():
                        statement["predicate"] = "have"
                statements.append(statement)
        
        return statements
    
    def _extract_definitions(self, message: str) -> List[Dict[str, str]]:
        """
        Extract definitions from a message.
        
        Args:
            message: The message to extract definitions from.
            
        Returns:
            A list of dictionaries, where each dictionary contains the term and
            definition.
        """
        definitions = []
        
        # Define patterns for extracting definitions
        patterns = [
            # "X is defined as Y" pattern
            r"(?P<term>\w+(?:\s+\w+)*)\s+is\s+defined\s+as\s+(?P<definition>.+)",
            # "X means Y" pattern
            r"(?P<term>\w+(?:\s+\w+)*)\s+means\s+(?P<definition>.+)",
            # "X refers to Y" pattern
            r"(?P<term>\w+(?:\s+\w+)*)\s+refers\s+to\s+(?P<definition>.+)",
            # "X is a Y that Z" pattern
            r"(?P<term>\w+(?:\s+\w+)*)\s+is\s+a\s+(?P<category>\w+(?:\s+\w+)*)\s+that\s+(?P<description>.+)"
        ]
        
        # Extract definitions using the patterns
        for pattern in patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                definition = match.groupdict()
                if "category" in definition and "description" in definition:
                    definition["definition"] = f"a {definition['category']} that {definition['description']}"
                definitions.append(definition)
        
        return definitions
    
    def _extract_relationships(self, message: str) -> List[Dict[str, str]]:
        """
        Extract relationships from a message.
        
        Args:
            message: The message to extract relationships from.
            
        Returns:
            A list of dictionaries, where each dictionary contains the subject,
            relation type, and object of a relationship.
        """
        relationships = []
        
        # Define patterns for extracting relationships
        patterns = [
            # "X is related to Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+related\s+to\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X is connected to Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+connected\s+to\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X is a type of Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+a\s+type\s+of\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X is a part of Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+a\s+part\s+of\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X belongs to Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+belongs\s+to\s+(?P<object>\w+(?:\s+\w+)*)"
        ]
        
        # Extract relationships using the patterns
        for pattern in patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                relationship = match.groupdict()
                if "is related to" in match.group():
                    relationship["relation_type"] = "related_to"
                elif "is connected to" in match.group():
                    relationship["relation_type"] = "connected_to"
                elif "is a type of" in match.group():
                    relationship["relation_type"] = "is_a"
                elif "is a part of" in match.group():
                    relationship["relation_type"] = "part_of"
                elif "belongs to" in match.group():
                    relationship["relation_type"] = "belongs_to"
                relationships.append(relationship)
        
        return relationships
    
    def _extract_properties(self, message: str) -> List[Dict[str, str]]:
        """
        Extract properties from a message.
        
        Args:
            message: The message to extract properties from.
            
        Returns:
            A list of dictionaries, where each dictionary contains the subject,
            property name, and property value.
        """
        properties = []
        
        # Define patterns for extracting properties
        patterns = [
            # "X has a Y of Z" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+has\s+a\s+(?P<property>\w+(?:\s+\w+)*)\s+of\s+(?P<value>\w+(?:\s+\w+)*)",
            # "X's Y is Z" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)'s\s+(?P<property>\w+(?:\s+\w+)*)\s+is\s+(?P<value>\w+(?:\s+\w+)*)",
            # "The Y of X is Z" pattern
            r"The\s+(?P<property>\w+(?:\s+\w+)*)\s+of\s+(?P<subject>\w+(?:\s+\w+)*)\s+is\s+(?P<value>\w+(?:\s+\w+)*)"
        ]
        
        # Extract properties using the patterns
        for pattern in patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                property_ = match.groupdict()
                properties.append(property_)
        
        return properties
    
    def _process_statement(self, statement: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a statement and update the Knowledge Graph.
        
        Args:
            statement: A dictionary containing the subject, predicate, and object
                of a statement.
                
        Returns:
            A dictionary containing the processing results.
        """
        subject = statement.get("subject")
        predicate = statement.get("predicate")
        object_ = statement.get("object")
        
        if not subject or not predicate or not object_:
            return {"success": False, "error": "Missing subject, predicate, or object in statement"}
        
        # Create an intent for the statement
        intent = Intent(
            type=IntentType.STATEMENT,
            confidence=1.0,
            entities={
                "subject": subject,
                "predicate": predicate,
                "object": object_
            },
            metadata={}
        )
        
        # Update the Knowledge Graph using the statement intent
        return self._handle_statement_intent(intent, None)
    
    def _process_definition(self, definition: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a definition and update the Knowledge Graph.
        
        Args:
            definition: A dictionary containing the term and definition.
                
        Returns:
            A dictionary containing the processing results.
        """
        term = definition.get("term")
        definition_text = definition.get("definition")
        
        if not term or not definition_text:
            return {"success": False, "error": "Missing term or definition"}
        
        # Get or create the concept node for the term
        concept = self.knowledge_graph.get_concept_by_name(term)
        if not concept:
            concept = self.knowledge_graph.add_concept(term)
        
        # Set the definition property
        concept.set_property("definition", definition_text)
        
        return {
            "success": True,
            "type": "definition",
            "term": term,
            "definition": definition_text
        }
    
    def _process_relationship(self, relationship: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a relationship and update the Knowledge Graph.
        
        Args:
            relationship: A dictionary containing the subject, relation type,
                and object of a relationship.
                
        Returns:
            A dictionary containing the processing results.
        """
        subject = relationship.get("subject")
        relation_type = relationship.get("relation_type")
        object_ = relationship.get("object")
        
        if not subject or not relation_type or not object_:
            return {"success": False, "error": "Missing subject, relation type, or object in relationship"}
        
        # Get or create the concept nodes for the subject and object
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            subject_concept = self.knowledge_graph.add_concept(subject)
        
        object_concept = self.knowledge_graph.get_concept_by_name(object_)
        if not object_concept:
            object_concept = self.knowledge_graph.add_concept(object_)
        
        # Create the relation
        self.knowledge_graph.update_relation(subject_concept, object_concept, relation_type)
        
        return {
            "success": True,
            "type": "relationship",
            "subject": subject,
            "relation_type": relation_type,
            "object": object_
        }
    
    def _process_property(self, property_: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a property and update the Knowledge Graph.
        
        Args:
            property_: A dictionary containing the subject, property name,
                and property value.
                
        Returns:
            A dictionary containing the processing results.
        """
        subject = property_.get("subject")
        property_name = property_.get("property")
        property_value = property_.get("value")
        
        if not subject or not property_name or not property_value:
            return {"success": False, "error": "Missing subject, property name, or property value"}
        
        # Get or create the concept node for the subject
        subject_concept = self.knowledge_graph.get_concept_by_name(subject)
        if not subject_concept:
            subject_concept = self.knowledge_graph.add_concept(subject)
        
        # Set the property
        subject_concept.set_property(property_name, property_value)
        
        return {
            "success": True,
            "type": "property",
            "subject": subject,
            "property": property_name,
            "value": property_value
        }