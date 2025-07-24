# Conversation Manager Implementation

The Conversation Manager is responsible for maintaining context across interactions and managing the conversation flow. This document provides a detailed implementation plan for this core component.

## Core Principles

The Conversation Manager is based on the following principles:

1. **Context Awareness**: The system maintains context across interactions to provide coherent conversations.
2. **Intent Recognition**: The system understands user intents to provide appropriate responses.
3. **Memory Management**: The system manages short-term and long-term conversation memory.
4. **Knowledge Integration**: The system integrates knowledge from the knowledge graph into conversations.
5. **External Connectivity**: The system can access external knowledge sources when needed.

## Core Components

### 1. Context Tracking

The Context Tracking system maintains conversation context and ensures coherence.

#### Implementation Details:

```python
class ConversationContext:
    def __init__(self, max_history=10):
        self.history = []  # List of (user_message, system_response) tuples
        self.max_history = max_history
        self.current_topic = None
        self.entities_mentioned = {}  # {entity: last_mention_index}
        self.intents_history = []  # List of recognized intents
        self.last_updated = time.time()
        self.creation_time = time.time()
        
    def add_exchange(self, user_message, system_response, intent=None, entities=None):
        """Add a new exchange to the conversation history."""
        # Add to history
        self.history.append((user_message, system_response))
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # Update intents history
        if intent:
            self.intents_history.append(intent)
            if len(self.intents_history) > self.max_history:
                self.intents_history.pop(0)
                
        # Update entities mentioned
        if entities:
            for entity in entities:
                self.entities_mentioned[entity] = len(self.history) - 1
                
        # Update timestamp
        self.last_updated = time.time()
        
    def get_recent_history(self, n=None):
        """Get the n most recent exchanges."""
        if n is None or n >= len(self.history):
            return self.history
        return self.history[-n:]
        
    def get_last_user_message(self):
        """Get the last user message."""
        if not self.history:
            return None
        return self.history[-1][0]
        
    def get_last_system_response(self):
        """Get the last system response."""
        if not self.history:
            return None
        return self.history[-1][1]
        
    def get_context_summary(self):
        """Get a summary of the current context."""
        if not self.history:
            return "No conversation history."
            
        # Create a summary of recent exchanges
        recent = self.get_recent_history(3)
        summary = "Recent exchanges:\n"
        for i, (user, system) in enumerate(recent):
            summary += f"User: {user}\nSystem: {system}\n"
            
        # Add information about current topic
        if self.current_topic:
            summary += f"\nCurrent topic: {self.current_topic}"
            
        # Add information about recently mentioned entities
        if self.entities_mentioned:
            recent_entities = sorted(self.entities_mentioned.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
            summary += "\nRecently mentioned entities: "
            summary += ", ".join([entity for entity, _ in recent_entities])
            
        return summary
```

### 2. Intent Recognition

The Intent Recognition system understands user queries and identifies their intent.

#### Implementation Details:

```python
class IntentRecognizer:
    def __init__(self, reasoning_core):
        self.reasoning_core = reasoning_core
        self.intent_patterns = self._initialize_intent_patterns()
        
    def _initialize_intent_patterns(self):
        """Initialize patterns for recognizing intents."""
        return {
            "greeting": [
                r"^(?:hello|hi|hey|greetings)(?:\s|$)",
                r"^good\s+(?:morning|afternoon|evening)(?:\s|$)"
            ],
            "farewell": [
                r"^(?:goodbye|bye|see\s+you|farewell)(?:\s|$)",
                r"^(?:have\s+a\s+(?:good|nice)\s+day)(?:\s|$)"
            ],
            "thanks": [
                r"^(?:thanks|thank\s+you|appreciate\s+it)(?:\s|$)"
            ],
            "help": [
                r"^(?:help|assist|support)(?:\s|$)",
                r"^(?:how\s+(?:can|do)\s+(?:you|I))(?:\s|$)",
                r"^(?:what\s+can\s+you\s+do)(?:\s|$)"
            ],
            "definition": [
                r"^(?:what\s+is|what\s+are|define|explain|describe)(?:\s|$)",
                r"^(?:tell\s+me\s+about)(?:\s|$)"
            ],
            "capability": [
                r"^(?:what\s+can|what\s+could|what\s+is\s+capable)(?:\s|$)",
                r"^(?:can\s+[a-z]+)(?:\s|$)"
            ],
            "verification": [
                r"^(?:is|are|was|were|do|does|did|has|have|had)(?:\s|$)",
                r"^(?:can\s+[a-z]+)(?:\s|$)"
            ],
            "comparison": [
                r"(?:compare|difference\s+between|similarities\s+between)(?:\s|$)",
                r"(?:how\s+(?:is|are)\s+[a-z]+\s+(?:different|similar)\s+to)(?:\s|$)"
            ],
            "location": [
                r"^(?:where\s+is|where\s+are|location\s+of)(?:\s|$)"
            ],
            "time": [
                r"^(?:when\s+is|when\s+are|time\s+of)(?:\s|$)"
            ],
            "reason": [
                r"^(?:why\s+is|why\s+are|reason\s+for)(?:\s|$)"
            ],
            "how_to": [
                r"^(?:how\s+to|how\s+do\s+I|steps\s+to)(?:\s|$)"
            ],
            "opinion": [
                r"^(?:what\s+do\s+you\s+think|your\s+opinion|do\s+you\s+believe)(?:\s|$)"
            ],
            "clarification": [
                r"^(?:what\s+do\s+you\s+mean|clarify|explain\s+again)(?:\s|$)"
            ],
            "correction": [
                r"^(?:no|incorrect|that's\s+wrong|not\s+right)(?:\s|$)"
            ]
        }
        
    def recognize_intent(self, text, context=None):
        """Recognize the intent of a user message."""
        # Normalize text
        normalized_text = text.lower().strip()
        
        # Check for pattern-based intents
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized_text):
                    return {
                        "intent": intent,
                        "confidence": 0.8,
                        "pattern_matched": pattern
                    }
        
        # Use the reasoning core for more complex intent recognition
        result = self.reasoning_core.reason(text, context)
        
        # Extract intent from reasoning result
        if "query_type" in result:
            return {
                "intent": result["query_type"],
                "confidence": result.get("confidence", 0.6),
                "reasoning_result": result
            }
            
        # Extract entities from the text
        entities = self._extract_entities(text)
        
        # Default to a generic intent
        return {
            "intent": "unknown",
            "confidence": 0.3,
            "entities": entities
        }
        
    def _extract_entities(self, text):
        """Extract entities from text."""
        # This would be replaced with a more sophisticated entity extraction
        entities = []
        
        # Simple regex-based entity extraction
        # Look for capitalized words (potential proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(proper_nouns)
        
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]*)"', text)
        entities.extend(quoted)
        
        return entities
```

### 3. Response Planning

The Response Planning system strategically plans responses based on context and goals.

#### Implementation Details:

```python
class ResponsePlanner:
    def __init__(self, reasoning_core, knowledge_graph):
        self.reasoning_core = reasoning_core
        self.knowledge_graph = knowledge_graph
        
    def plan_response(self, user_message, intent_data, context):
        """Plan a response based on the user's message, intent, and context."""
        intent = intent_data.get("intent", "unknown")
        
        # Handle different intents
        if intent == "greeting":
            return self._plan_greeting_response(context)
            
        elif intent == "farewell":
            return self._plan_farewell_response(context)
            
        elif intent == "thanks":
            return self._plan_thanks_response(context)
            
        elif intent == "help":
            return self._plan_help_response(context)
            
        elif intent == "definition":
            return self._plan_definition_response(user_message, intent_data, context)
            
        elif intent == "capability":
            return self._plan_capability_response(user_message, intent_data, context)
            
        elif intent == "verification":
            return self._plan_verification_response(user_message, intent_data, context)
            
        elif intent == "comparison":
            return self._plan_comparison_response(user_message, intent_data, context)
            
        elif intent == "clarification":
            return self._plan_clarification_response(context)
            
        elif intent == "correction":
            return self._plan_correction_response(context)
            
        else:
            # Use the reasoning core for general responses
            reasoning_result = self.reasoning_core.reason(user_message, context.get_context_summary())
            
            # Generate a response based on the reasoning result
            response = self.reasoning_core.response_generator.generate_response(reasoning_result, user_message)
            
            return {
                "response_type": "general",
                "response_text": response,
                "reasoning_result": reasoning_result
            }
            
    def _plan_greeting_response(self, context):
        """Plan a greeting response."""
        # Check if this is the first interaction
        if not context.history:
            return {
                "response_type": "greeting",
                "response_text": "Hello! I'm CCAI, a cognitive concept AI. How can I help you today?"
            }
            
        # Check if we've already greeted the user recently
        recent_intents = context.intents_history[-3:] if context.intents_history else []
        if "greeting" in recent_intents:
            return {
                "response_type": "greeting",
                "response_text": "Hello again! What can I help you with?"
            }
            
        # Standard greeting
        return {
            "response_type": "greeting",
            "response_text": "Hello! How can I assist you today?"
        }
        
    def _plan_farewell_response(self, context):
        """Plan a farewell response."""
        return {
            "response_type": "farewell",
            "response_text": "Goodbye! Feel free to return if you have more questions."
        }
        
    def _plan_thanks_response(self, context):
        """Plan a response to thanks."""
        return {
            "response_type": "thanks",
            "response_text": "You're welcome! Is there anything else I can help with?"
        }
        
    def _plan_help_response(self, context):
        """Plan a help response."""
        return {
            "response_type": "help",
            "response_text": "I can answer questions about various topics, define concepts, verify relationships, and explain capabilities. What would you like to know about?"
        }
        
    def _plan_definition_response(self, user_message, intent_data, context):
        """Plan a definition response."""
        # Extract the entity to define
        entity = self._extract_definition_entity(user_message)
        
        if not entity:
            return {
                "response_type": "clarification",
                "response_text": "I'm not sure what you'd like me to define. Could you specify the concept you're interested in?"
            }
            
        # Check if we have knowledge about this entity
        node = self.knowledge_graph.get_node(entity)
        
        if node:
            # Use the knowledge graph to generate a definition
            definition_data = {
                "entity": entity,
                "response_type": "definition"
            }
            
            # Get is_a relations
            is_a_relations = node.get_relations("is_a")
            if is_a_relations:
                definition_data["is_a"] = [rel.target for _, rel in is_a_relations]
                
            # Get properties
            properties = node.get_property("property")
            if properties:
                definition_data["properties"] = [prop.value for prop in properties]
                
            # Get capabilities
            can_do_relations = node.get_relations("can_do")
            if can_do_relations:
                definition_data["capabilities"] = [rel.target for _, rel in can_do_relations]
                
            # Get parts
            has_part_relations = node.get_relations("has_part")
            if has_part_relations:
                definition_data["parts"] = [rel.target for _, rel in has_part_relations]
                
            # Generate response using the reasoning core
            reasoning_result = self.reasoning_core.reason(f"what is {entity}", context.get_context_summary())
            response = self.reasoning_core.response_generator.generate_response(reasoning_result, user_message)
            
            return {
                "response_type": "definition",
                "response_text": response,
                "entity": entity,
                "definition_data": definition_data,
                "reasoning_result": reasoning_result
            }
        else:
            # We don't have knowledge about this entity
            return {
                "response_type": "unknown_entity",
                "response_text": f"I don't have information about '{entity}' in my knowledge base. Would you like me to search for external information?",
                "entity": entity
            }
            
    def _plan_capability_response(self, user_message, intent_data, context):
        """Plan a capability response."""
        # Extract the entity
        entity = self._extract_capability_entity(user_message)
        
        if not entity:
            return {
                "response_type": "clarification",
                "response_text": "I'm not sure which entity you're asking about capabilities for. Could you specify?"
            }
            
        # Check if we have knowledge about this entity
        node = self.knowledge_graph.get_node(entity)
        
        if node:
            # Use the knowledge graph to get capabilities
            capability_data = {
                "entity": entity,
                "response_type": "capability"
            }
            
            # Get capabilities
            can_do_relations = node.get_relations("can_do")
            if can_do_relations:
                capability_data["capabilities"] = [rel.target for _, rel in can_do_relations]
                
            # Generate response using the reasoning core
            reasoning_result = self.reasoning_core.reason(f"what can {entity} do", context.get_context_summary())
            response = self.reasoning_core.response_generator.generate_response(reasoning_result, user_message)
            
            return {
                "response_type": "capability",
                "response_text": response,
                "entity": entity,
                "capability_data": capability_data,
                "reasoning_result": reasoning_result
            }
        else:
            # We don't have knowledge about this entity
            return {
                "response_type": "unknown_entity",
                "response_text": f"I don't have information about '{entity}' in my knowledge base. Would you like me to search for external information?",
                "entity": entity
            }
            
    def _plan_verification_response(self, user_message, intent_data, context):
        """Plan a verification response."""
        # Extract the subject and target
        subject, target = self._extract_verification_parts(user_message)
        
        if not subject or not target:
            return {
                "response_type": "clarification",
                "response_text": "I'm not sure what you're asking me to verify. Could you rephrase your question?"
            }
            
        # Check if we have knowledge about the subject
        subject_node = self.knowledge_graph.get_node(subject)
        
        if subject_node:
            # Use the knowledge graph to verify the relationship
            verification_data = {
                "entity": subject,
                "response_type": "verification",
                "target": target,
                "relation": "is_a"  # Default relation
            }
            
            # Determine the relation type based on the question
            if "can" in user_message.lower():
                verification_data["relation"] = "can_do"
            elif "has" in user_message.lower() or "have" in user_message.lower():
                verification_data["relation"] = "has_part"
                
            # Check for the relation
            relations = subject_node.get_relations(verification_data["relation"])
            verification_data["verified"] = any(rel.target == target for _, rel in relations)
            
            # Generate response using the reasoning core
            reasoning_result = self.reasoning_core.reason(user_message, context.get_context_summary())
            response = self.reasoning_core.response_generator.generate_response(reasoning_result, user_message)
            
            return {
                "response_type": "verification",
                "response_text": response,
                "subject": subject,
                "target": target,
                "relation": verification_data["relation"],
                "verified": verification_data["verified"],
                "reasoning_result": reasoning_result
            }
        else:
            # We don't have knowledge about this subject
            return {
                "response_type": "unknown_entity",
                "response_text": f"I don't have information about '{subject}' in my knowledge base. Would you like me to search for external information?",
                "entity": subject
            }
            
    def _plan_comparison_response(self, user_message, intent_data, context):
        """Plan a comparison response."""
        # Extract the entities to compare
        entity1, entity2 = self._extract_comparison_entities(user_message)
        
        if not entity1 or not entity2:
            return {
                "response_type": "clarification",
                "response_text": "I'm not sure which entities you want me to compare. Could you specify?"
            }
            
        # Check if we have knowledge about both entities
        node1 = self.knowledge_graph.get_node(entity1)
        node2 = self.knowledge_graph.get_node(entity2)
        
        if node1 and node2:
            # Use the knowledge graph to compare the entities
            comparison_data = {
                "entity1": entity1,
                "entity2": entity2,
                "response_type": "comparison"
            }
            
            # Find similarities
            similarities = []
            
            # Check for common is_a relations
            is_a1 = {rel.target for _, rel in node1.get_relations("is_a")}
            is_a2 = {rel.target for _, rel in node2.get_relations("is_a")}
            common_categories = is_a1 & is_a2
            
            if common_categories:
                similarities.append(f"Both are {', '.join(common_categories)}.")
                
            # Check for common capabilities
            can_do1 = {rel.target for _, rel in node1.get_relations("can_do")}
            can_do2 = {rel.target for _, rel in node2.get_relations("can_do")}
            common_capabilities = can_do1 & can_do2
            
            if common_capabilities:
                similarities.append(f"Both can {', '.join(common_capabilities)}.")
                
            # Check for common parts
            has_part1 = {rel.target for _, rel in node1.get_relations("has_part")}
            has_part2 = {rel.target for _, rel in node2.get_relations("has_part")}
            common_parts = has_part1 & has_part2
            
            if common_parts:
                similarities.append(f"Both have {', '.join(common_parts)}.")
                
            comparison_data["similarities"] = similarities
            
            # Find differences
            differences = []
            
            # Different categories
            diff_categories1 = is_a1 - is_a2
            if diff_categories1:
                differences.append(f"{entity1} is {', '.join(diff_categories1)}, but {entity2} is not.")
                
            diff_categories2 = is_a2 - is_a1
            if diff_categories2:
                differences.append(f"{entity2} is {', '.join(diff_categories2)}, but {entity1} is not.")
                
            # Different capabilities
            diff_capabilities1 = can_do1 - can_do2
            if diff_capabilities1:
                differences.append(f"{entity1} can {', '.join(diff_capabilities1)}, but {entity2} cannot.")
                
            diff_capabilities2 = can_do2 - can_do1
            if diff_capabilities2:
                differences.append(f"{entity2} can {', '.join(diff_capabilities2)}, but {entity1} cannot.")
                
            # Different parts
            diff_parts1 = has_part1 - has_part2
            if diff_parts1:
                differences.append(f"{entity1} has {', '.join(diff_parts1)}, but {entity2} does not.")
                
            diff_parts2 = has_part2 - has_part1
            if diff_parts2:
                differences.append(f"{entity2} has {', '.join(diff_parts2)}, but {entity1} does not.")
                
            comparison_data["differences"] = differences
            
            # Generate response
            response = f"Comparing {entity1} and {entity2}:\n\n"
            
            if similarities:
                response += "Similarities:\n"
                response += "\n".join(f"- {sim}" for sim in similarities)
                response += "\n\n"
                
            if differences:
                response += "Differences:\n"
                response += "\n".join(f"- {diff}" for diff in differences)
                
            if not similarities and not differences:
                response += "I don't have enough information to compare these entities in detail."
                
            return {
                "response_type": "comparison",
                "response_text": response,
                "entity1": entity1,
                "entity2": entity2,
                "comparison_data": comparison_data
            }
        else:
            # We don't have knowledge about one or both entities
            missing = []
            if not node1:
                missing.append(entity1)
            if not node2:
                missing.append(entity2)
                
            return {
                "response_type": "unknown_entity",
                "response_text": f"I don't have information about {', '.join(missing)} in my knowledge base. Would you like me to search for external information?",
                "missing_entities": missing
            }
            
    def _plan_clarification_response(self, context):
        """Plan a clarification response."""
        # Get the last system response
        last_response = context.get_last_system_response()
        
        if not last_response:
            return {
                "response_type": "clarification",
                "response_text": "I'm not sure what you're asking for clarification about. Could you provide more details?"
            }
            
        return {
            "response_type": "clarification",
            "response_text": f"Let me clarify my previous response. {last_response} Is there a specific part you'd like me to explain further?"
        }
        
    def _plan_correction_response(self, context):
        """Plan a response to a correction."""
        return {
            "response_type": "correction",
            "response_text": "I apologize for the error. Could you please explain what was incorrect in my response so I can provide better information?"
        }
        
    def _extract_definition_entity(self, text):
        """Extract the entity to define from text."""
        # This would be replaced with a more sophisticated parser
        patterns = [
            r"what is (?:a |an )?([a-z ]+)(?:\?|$)",
            r"what are (?:a |an )?([a-z ]+)(?:\?|$)",
            r"define (?:a |an )?([a-z ]+)(?:\?|$)",
            r"explain (?:a |an )?([a-z ]+)(?:\?|$)",
            r"describe (?:a |an )?([a-z ]+)(?:\?|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
                
        return None
        
    def _extract_capability_entity(self, text):
        """Extract the entity for capability query from text."""
        # This would be replaced with a more sophisticated parser
        patterns = [
            r"what can (?:a |an )?([a-z ]+) do(?:\?|$)",
            r"what (?:is|are) (?:a |an )?([a-z ]+) capable of(?:\?|$)",
            r"can (?:a |an )?([a-z ]+) ([a-z ]+)(?:\?|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
                
        return None
        
    def _extract_verification_parts(self, text):
        """Extract subject and target from verification query."""
        # This would be replaced with a more sophisticated parser
        patterns = [
            r"is (?:a |an )?([a-z ]+) (?:a |an )?([a-z ]+)(?:\?|$)",
            r"are (?:a |an )?([a-z ]+) (?:a |an )?([a-z ]+)(?:\?|$)",
            r"can (?:a |an )?([a-z ]+) ([a-z ]+)(?:\?|$)",
            r"does (?:a |an )?([a-z ]+) have (?:a |an )?([a-z ]+)(?:\?|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip(), match.group(2).strip()
                
        return None, None
        
    def _extract_comparison_entities(self, text):
        """Extract entities for comparison from text."""
        # This would be replaced with a more sophisticated parser
        patterns = [
            r"compare (?:a |an )?([a-z ]+) (?:and|to) (?:a |an )?([a-z ]+)(?:\?|$)",
            r"difference between (?:a |an )?([a-z ]+) and (?:a |an )?([a-z ]+)(?:\?|$)",
            r"similarities between (?:a |an )?([a-z ]+) and (?:a |an )?([a-z ]+)(?:\?|$)",
            r"how (?:is|are) (?:a |an )?([a-z ]+) (?:different|similar) to (?:a |an )?([a-z ]+)(?:\?|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip(), match.group(2).strip()
                
        return None, None
```

### 4. Memory Management

The Memory Management system manages short-term and long-term conversation memory.

#### Implementation Details:

```python
class MemoryManager:
    def __init__(self, max_short_term=10, max_long_term=100):
        self.short_term_memory = []  # Recent exchanges
        self.long_term_memory = []  # Important exchanges
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.entity_mentions = {}  # {entity: [mention_indices]}
        self.topic_history = []  # List of (topic, start_index, end_index)
        
    def add_exchange(self, user_message, system_response, intent=None, entities=None, importance=0.5):
        """Add a new exchange to memory."""
        # Create exchange record
        exchange = {
            "user_message": user_message,
            "system_response": system_response,
            "intent": intent,
            "entities": entities or [],
            "timestamp": time.time(),
            "importance": importance,
            "index": len(self.short_term_memory)
        }
        
        # Add to short-term memory
        self.short_term_memory.append(exchange)
        
        # Trim short-term memory if needed
        if len(self.short_term_memory) > self.max_short_term:
            # Move oldest exchange to long-term memory if important enough
            oldest = self.short_term_memory.pop(0)
            if oldest["importance"] > 0.7:
                self.long_term_memory.append(oldest)
                
                # Trim long-term memory if needed
                if len(self.long_term_memory) > self.max_long_term:
                    # Remove least important exchange
                    least_important_idx = min(range(len(self.long_term_memory)), 
                                            key=lambda i: self.long_term_memory[i]["importance"])
                    self.long_term_memory.pop(least_important_idx)
                    
        # Update entity mentions
        if entities:
            for entity in entities:
                if entity not in self.entity_mentions:
                    self.entity_mentions[entity] = []
                self.entity_mentions[entity].append(exchange["index"])
                
        # Update topic if needed
        self._update_topic(exchange)
        
    def get_recent_exchanges(self, n=None):
        """Get the n most recent exchanges."""
        if n is None or n >= len(self.short_term_memory):
            return self.short_term_memory
        return self.short_term_memory[-n:]
        
    def get_entity_history(self, entity, max_exchanges=5):
        """Get exchanges where an entity was mentioned."""
        if entity not in self.entity_mentions:
            return []
            
        # Get indices of mentions
        indices = self.entity_mentions[entity]
        
        # Get exchanges for these indices
        exchanges = []
        for idx in indices:
            # Check short-term memory
            for exchange in self.short_term_memory:
                if exchange["index"] == idx:
                    exchanges.append(exchange)
                    break
                    
            # Check long-term memory if not found
            if len(exchanges