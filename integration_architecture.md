# Integration Architecture

This document outlines how the three core components of the new CCAI Engine architecture - the Unified Reasoning Core, Knowledge Graph, and Conversation Manager - are integrated to create a truly intelligent system.

## Overview

The integration architecture is designed to be simple, elegant, and powerful. The three core components work together through well-defined interfaces, with each component focusing on its specific responsibilities while collaborating to provide a seamless experience.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CCAI Engine                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 Unified Reasoning Core                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ▲                                  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │                 │    │                                  │   │
│  │  Knowledge      │◄──►│       Conversation Manager       │   │
│  │  Graph          │    │                                  │   │
│  │                 │    │                                  │   │
│  └─────────────────┘    └──────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Interfaces

### 1. Unified Reasoning Core ↔ Knowledge Graph

The Unified Reasoning Core and Knowledge Graph are integrated through the `KnowledgeInterface` class, which provides methods for:

1. **Retrieving Ideom Connections**: The Reasoning Core can retrieve connections for ideoms from the Knowledge Graph.
2. **Learning from Ideom Activations**: The Knowledge Graph can learn from ideom activations in the Reasoning Core.
3. **Querying Knowledge**: The Reasoning Core can query the Knowledge Graph for information.
4. **Updating Knowledge**: The Reasoning Core can update the Knowledge Graph with new knowledge.

```python
class KnowledgeInterface:
    def __init__(self, knowledge_graph, reasoning_core):
        self.graph = knowledge_graph
        self.core = reasoning_core
        
    def get_ideom_connections(self, ideom_name):
        """Get connections for an ideom from the knowledge graph."""
        node = self.graph.get_node(ideom_name)
        if not node:
            return {}
            
        connections = {}
        
        # Add connections from relations
        for rel_type, relations in node.relations.items():
            for rel in relations:
                connections[rel.target] = rel.confidence
                
        return connections
        
    def learn_from_ideom_activations(self, activated_ideoms):
        """Learn from ideom activations in the reasoning core."""
        # Create or strengthen connections between co-activated ideoms
        ideom_names = list(activated_ideoms.keys())
        for i, name1 in enumerate(ideom_names):
            for name2 in ideom_names[i+1:]:
                # Only connect if both are sufficiently activated
                activation1 = activated_ideoms[name1].activation
                activation2 = activated_ideoms[name2].activation
                
                if activation1 > 0.3 and activation2 > 0.3:
                    # Add or strengthen relation in knowledge graph
                    self.graph.add_relation(name1, "related_to", name2, 
                                          min(activation1, activation2))
                    
    def query_knowledge(self, query_type, params):
        """Query the knowledge graph from the reasoning core."""
        return self.graph.query(query_type, params)
        
    def update_knowledge(self, knowledge):
        """Update the knowledge graph from the reasoning core."""
        self.graph.learn(knowledge)
        
    def sync_ideoms_to_knowledge(self):
        """Synchronize ideoms in the reasoning core with the knowledge graph."""
        # For each node in the knowledge graph
        for node_name, node in self.graph.nodes.items():
            # Create or update corresponding ideom
            if node_name not in self.core.ideom_network:
                self.core.add_ideom(node_name, node.ctype)
            
            # Sync connections
            ideom = self.core.ideom_network[node_name]
            
            # Add connections from relations
            for rel_type, relations in node.relations.items():
                for rel in relations:
                    if rel.target in self.core.ideom_network:
                        ideom.connect(rel.target, rel.confidence)
                        
    def sync_knowledge_to_ideoms(self):
        """Synchronize knowledge graph with ideoms in the reasoning core."""
        # For each ideom in the reasoning core
        for ideom_name, ideom in self.core.ideom_network.items():
            # Create or update corresponding node
            if not self.graph.get_node(ideom_name):
                self.graph.add_node(ideom_name, ideom.category)
            
            # Sync connections
            for connected_name, strength in ideom.connections.items():
                if connected_name in self.core.ideom_network:
                    self.graph.add_relation(ideom_name, "related_to", connected_name, strength)
```

### 2. Unified Reasoning Core ↔ Conversation Manager

The Unified Reasoning Core and Conversation Manager are integrated through the `ReasoningInterface` class, which provides methods for:

1. **Processing User Messages**: The Conversation Manager can process user messages through the Reasoning Core.
2. **Generating Responses**: The Conversation Manager can generate responses using the Reasoning Core.
3. **Learning from Conversations**: The Reasoning Core can learn from conversations managed by the Conversation Manager.
4. **Accessing Context**: The Reasoning Core can access conversation context from the Conversation Manager.

```python
class ReasoningInterface:
    def __init__(self, reasoning_core, conversation_manager):
        self.core = reasoning_core
        self.manager = conversation_manager
        
    def process_message(self, user_message):
        """Process a user message through the reasoning core."""
        # Get conversation context
        context = self.manager.get_context_summary()
        
        # Process through reasoning core
        result = self.core.reason(user_message, context)
        
        # Extract entities and intent
        entities = self._extract_entities(result)
        intent = self._extract_intent(result)
        
        return {
            "reasoning_result": result,
            "entities": entities,
            "intent": intent
        }
        
    def generate_response(self, reasoning_result, user_message):
        """Generate a response using the reasoning core."""
        return self.core.response_generator.generate_response(reasoning_result, user_message)
        
    def learn_from_conversation(self, user_message, system_response, reasoning_result):
        """Learn from a conversation exchange."""
        # Extract activated ideoms
        activated_ideoms = self.core.signal_propagator.get_activated_ideoms()
        
        # Learn from activation
        self.core.learning_mechanism.learn_from_activation(activated_ideoms)
        
        # Add to experience buffer
        self.core.learning_mechanism.add_to_experience_buffer(activated_ideoms, reasoning_result)
        
        # Periodically learn from buffer
        if random.random() < 0.2:  # 20% chance
            self.core.learning_mechanism.learn_from_buffer()
            
    def get_context_for_reasoning(self):
        """Get conversation context for reasoning."""
        return self.manager.get_context_summary()
        
    def _extract_entities(self, reasoning_result):
        """Extract entities from reasoning result."""
        entities = []
        
        # Extract from top ideoms
        if "top_ideoms" in reasoning_result:
            entities.extend([name for name, _ in reasoning_result["top_ideoms"] 
                           if self._is_entity(name)])
                           
        # Extract from top prefabs
        if "top_prefabs" in reasoning_result:
            for name, _ in reasoning_result["top_prefabs"]:
                prefab = self.core.prefab_manager.prefabs.get(name)
                if prefab:
                    entities.extend([ideom_name for ideom_name in prefab.pattern.keys() 
                                   if self._is_entity(ideom_name)])
                                   
        return list(set(entities))  # Remove duplicates
        
    def _extract_intent(self, reasoning_result):
        """Extract intent from reasoning result."""
        # Check for query type
        if "query_type" in reasoning_result:
            return reasoning_result["query_type"]
            
        # Check for result type
        if "result" in reasoning_result:
            return reasoning_result["result"]
            
        # Default to unknown
        return "unknown"
        
    def _is_entity(self, name):
        """Check if an ideom name represents an entity."""
        ideom = self.core.ideom_network.get(name)
        if not ideom:
            return False
            
        # Check category
        return ideom.category in ["entity", "object", "agent"]
```

### 3. Knowledge Graph ↔ Conversation Manager

The Knowledge Graph and Conversation Manager are integrated through the `ConversationKnowledgeInterface` class, which provides methods for:

1. **Retrieving Entity Information**: The Conversation Manager can retrieve information about entities from the Knowledge Graph.
2. **Learning from Conversations**: The Knowledge Graph can learn from conversations managed by the Conversation Manager.
3. **Finding Related Entities**: The Conversation Manager can find entities related to the current conversation from the Knowledge Graph.
4. **Resolving References**: The Conversation Manager can resolve references in the conversation using the Knowledge Graph.

```python
class ConversationKnowledgeInterface:
    def __init__(self, knowledge_graph, conversation_manager):
        self.graph = knowledge_graph
        self.manager = conversation_manager
        
    def get_entity_information(self, entity_name):
        """Get information about an entity from the knowledge graph."""
        node = self.graph.get_node(entity_name)
        if not node:
            return None
            
        # Collect information about the entity
        info = {
            "name": node.name,
            "type": node.ctype,
            "aliases": node.aliases,
            "properties": {},
            "relations": {}
        }
        
        # Add properties
        for prop_name, props in node.properties.items():
            info["properties"][prop_name] = [
                {"value": prop.value, "confidence": prop.confidence}
                for prop in props
            ]
            
        # Add relations
        for rel_type, rels in node.relations.items():
            info["relations"][rel_type] = [
                {"target": rel.target, "confidence": rel.confidence}
                for rel in rels
            ]
            
        return info
        
    def learn_from_conversation(self, user_message, system_response, entities, intent):
        """Learn from a conversation exchange."""
        # Extract knowledge from the exchange
        knowledge = []
        
        # Learn about mentioned entities
        for entity in entities:
            # Check if this is a new entity
            if not self.graph.get_node(entity):
                # Add the entity
                self.graph.add_node(entity)
                
                # Add relation to the intent
                if intent != "unknown":
                    self.graph.add_relation(entity, "related_to", intent, 0.7)
                    
            # Learn from co-occurring entities
            for other_entity in entities:
                if entity != other_entity:
                    self.graph.add_relation(entity, "co_occurs_with", other_entity, 0.6)
                    
        # Try to extract more structured knowledge
        # This would be replaced with a more sophisticated knowledge extraction
        if intent == "definition" and len(entities) >= 2:
            # Possible definition: "X is a Y"
            self.graph.add_relation(entities[0], "is_a", entities[1], 0.7)
            
        elif intent == "capability" and len(entities) >= 2:
            # Possible capability: "X can Y"
            self.graph.add_relation(entities[0], "can_do", entities[1], 0.7)
            
        elif intent == "verification" and len(entities) >= 2:
            # Possible verification: "X is a Y" or "X can Y"
            if "is" in user_message.lower():
                self.graph.add_relation(entities[0], "is_a", entities[1], 0.7)
            elif "can" in user_message.lower():
                self.graph.add_relation(entities[0], "can_do", entities[1], 0.7)
                
        return knowledge
        
    def find_related_entities(self, entities, max_results=5):
        """Find entities related to the current conversation."""
        if not entities:
            return []
            
        related = {}
        
        for entity in entities:
            # Get node
            node = self.graph.get_node(entity)
            if not node:
                continue
                
            # Get related entities
            for rel_type, rels in node.relations.items():
                for rel in rels:
                    if rel.target not in entities and rel.target not in related:
                        related[rel.target] = rel.confidence
                        
        # Sort by confidence
        sorted_related = sorted(related.items(), key=lambda x: x[1], reverse=True)
        
        # Return top results
        return [entity for entity, _ in sorted_related[:max_results]]
        
    def resolve_reference(self, reference, context):
        """Resolve a reference in the conversation."""
        # This would be replaced with a more sophisticated reference resolution
        
        # Check for pronouns
        if reference.lower() in ["it", "this", "that"]:
            # Get recently mentioned entities
            recent_entities = self.manager.get_recent_entities(1)
            if recent_entities:
                return recent_entities[0]
                
        elif reference.lower() in ["they", "them", "these", "those"]:
            # Get recently mentioned entities
            recent_entities = self.manager.get_recent_entities(3)
            if recent_entities:
                return recent_entities
                
        # Check for partial matches
        nodes = self.graph.nodes
        for node_name in nodes:
            if reference.lower() in node_name.lower():
                return node_name
                
        # No resolution found
        return None
```

## Integration Flow

The integration of the three core components follows a clear flow:

1. **User Message Processing**:
   - The Conversation Manager receives a user message.
   - It uses the ReasoningInterface to process the message through the Unified Reasoning Core.
   - The Reasoning Core uses the KnowledgeInterface to access knowledge from the Knowledge Graph.
   - The Reasoning Core returns a reasoning result to the Conversation Manager.

2. **Response Generation**:
   - The Conversation Manager uses the ReasoningInterface to generate a response based on the reasoning result.
   - The Reasoning Core generates a response and returns it to the Conversation Manager.
   - The Conversation Manager formats and delivers the response to the user.

3. **Learning and Adaptation**:
   - After each exchange, the Conversation Manager uses the ConversationKnowledgeInterface to update the Knowledge Graph.
   - The Conversation Manager also uses the ReasoningInterface to update the Unified Reasoning Core.
   - Both the Knowledge Graph and Unified Reasoning Core learn from the exchange and adapt their behavior.

## Main Integration Class

The `CCAIEngine` class serves as the main integration point for the three core components:

```python
class CCAIEngine:
    def __init__(self, storage_path=None):
        # Initialize core components
        self.reasoning_core = UnifiedReasoningCore()
        self.knowledge_graph = KnowledgeGraph(storage_path)
        self.conversation_manager = ConversationManager()
        
        # Initialize interfaces
        self.knowledge_interface = KnowledgeInterface(self.knowledge_graph, self.reasoning_core)
        self.reasoning_interface = ReasoningInterface(self.reasoning_core, self.conversation_manager)
        self.conversation_knowledge_interface = ConversationKnowledgeInterface(
            self.knowledge_graph, self.conversation_manager)
            
        # Connect components
        self.reasoning_core.knowledge_interface = self.knowledge_interface
        self.conversation_manager.reasoning_interface = self.reasoning_interface
        self.conversation_manager.knowledge_interface = self.conversation_knowledge_interface
        
    def process_message(self, user_message):
        """Process a user message and generate a response."""
        # Process through conversation manager
        response = self.conversation_manager.process_message(user_message)
        
        # Return the response
        return response
        
    def learn(self, text):
        """Learn from text."""
        # Extract knowledge
        knowledge = self.reasoning_core.extract_knowledge(text)
        
        # Update knowledge graph
        self.knowledge_graph.learn(knowledge)
        
    def save(self):
        """Save the engine state."""
        self.knowledge_graph.save()
        
    def load(self):
        """Load the engine state."""
        self.knowledge_graph.load()
        
        # Sync knowledge graph with reasoning core
        self.knowledge_interface.sync_ideoms_to_knowledge()
```

## Conversation Flow Example

Here's an example of how the three components work together to process a user message and generate a response:

1. User sends a message: "What is a dog?"
2. The `CCAIEngine` receives the message and passes it to the `ConversationManager`.
3. The `ConversationManager` uses the `ReasoningInterface` to process the message through the `UnifiedReasoningCore`.
4. The `UnifiedReasoningCore` activates ideoms for "what", "is", "dog", etc.
5. The `UnifiedReasoningCore` uses the `KnowledgeInterface` to retrieve knowledge about "dog" from the `KnowledgeGraph`.
6. The `UnifiedReasoningCore` propagates activation through the ideom network and activates relevant prefabs.
7. The `UnifiedReasoningCore` generates a reasoning result and returns it to the `ConversationManager`.
8. The `ConversationManager` uses the `ReasoningInterface` to generate a response based on the reasoning result.
9. The `ConversationManager` adds the exchange to its context and returns the response to the user.
10. After the exchange, the `ConversationManager` uses the `ConversationKnowledgeInterface` to update the `KnowledgeGraph` with any new knowledge.
11. The `ConversationManager` also uses the `ReasoningInterface` to update the `UnifiedReasoningCore` with the exchange.

## Conclusion

The integration architecture provides a simple, elegant, and powerful way to combine the three core components of the new CCAI Engine. By focusing on clear interfaces and responsibilities, the architecture enables the components to work together seamlessly while maintaining their independence and specialization.

This approach allows for:

1. **Modularity**: Components can be developed and tested independently.
2. **Flexibility**: Components can be replaced or upgraded without affecting the others.
3. **Scalability**: The architecture can scale to handle more complex tasks and larger knowledge bases.
4. **Adaptability**: The system can learn and adapt over time through the integration of the components.

The result is a truly intelligent system that can understand, reason, learn, and communicate in a natural and effective way.