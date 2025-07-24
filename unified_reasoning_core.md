# Unified Reasoning Core Implementation

The Unified Reasoning Core is the heart of the new CCAI Engine architecture. This document provides a detailed implementation plan for this core component.

## Core Principles

The Unified Reasoning Core is based on the following principles:

1. **Ideom-Based Cognition**: Atomic units of cognition (ideoms) form the basis of all knowledge and reasoning.
2. **Signal Propagation**: Signals propagate through the ideom network, activating related concepts.
3. **Prefab Activation**: Patterns of ideom activation trigger higher-level prefabs.
4. **Dynamic Learning**: The system continuously learns from experience, adjusting ideom connections and creating new prefabs.
5. **Integrated Reasoning**: Reasoning is integrated with learning and generation, not a separate process.

## Core Components

### 1. Ideom Network

The Ideom Network is a dynamic network of ideoms (atomic units of cognition) that form the foundation of the system's knowledge.

#### Implementation Details:

```python
class Ideom:
    def __init__(self, name, category=None):
        self.name = name
        self.category = category
        self.activation = 0.0
        self.connections = {}  # {ideom_name: connection_strength}
        self.last_activated = 0  # Timestamp
        self.activation_count = 0  # How many times activated
        self.creation_time = time.time()
        
    def connect(self, other_ideom, strength=0.1):
        """Create or strengthen a connection to another ideom."""
        if other_ideom in self.connections:
            # Strengthen existing connection (with a cap)
            self.connections[other_ideom] = min(1.0, self.connections[other_ideom] + strength)
        else:
            # Create new connection
            self.connections[other_ideom] = strength
            
    def activate(self, strength=1.0):
        """Activate this ideom with the given strength."""
        self.activation = min(1.0, self.activation + strength)
        self.last_activated = time.time()
        self.activation_count += 1
        
    def decay(self, rate=0.1):
        """Decay the activation of this ideom."""
        self.activation = max(0.0, self.activation - rate)
```

### 2. Signal Propagation

The Signal Propagation mechanism simulates the spread of activation through the ideom network.

#### Implementation Details:

```python
class SignalPropagator:
    def __init__(self, ideom_network, decay_rate=0.1, threshold=0.1):
        self.ideom_network = ideom_network
        self.decay_rate = decay_rate
        self.threshold = threshold
        
    def propagate(self, iterations=3):
        """Propagate activation through the network for a number of iterations."""
        for _ in range(iterations):
            # Store current activations to avoid immediate feedback
            current_activations = {name: ideom.activation 
                                  for name, ideom in self.ideom_network.items()}
            
            # Propagate activation to connected ideoms
            for ideom_name, ideom in self.ideom_network.items():
                if current_activations[ideom_name] > self.threshold:
                    for connected_name, strength in ideom.connections.items():
                        if connected_name in self.ideom_network:
                            propagated_activation = current_activations[ideom_name] * strength
                            self.ideom_network[connected_name].activate(propagated_activation)
            
            # Apply decay to all ideoms
            for ideom in self.ideom_network.values():
                ideom.decay(self.decay_rate)
                
    def get_activated_ideoms(self, threshold=None):
        """Get all ideoms activated above the threshold."""
        if threshold is None:
            threshold = self.threshold
            
        return {name: ideom for name, ideom in self.ideom_network.items() 
                if ideom.activation > threshold}
```

### 3. Prefab System

The Prefab System recognizes patterns in the ideom network and activates higher-level concepts.

#### Implementation Details:

```python
class Prefab:
    def __init__(self, name, pattern, category=None, threshold=0.15):
        self.name = name
        self.pattern = pattern  # {ideom_name: required_activation}
        self.category = category
        self.threshold = threshold
        self.activation = 0.0
        self.last_activated = 0
        self.activation_count = 0
        self.creation_time = time.time()
        
    def compute_activation(self, ideom_network):
        """Compute the activation level based on the pattern match."""
        if not self.pattern:
            return 0.0
            
        total_weight = sum(self.pattern.values())
        if total_weight == 0:
            return 0.0
            
        weighted_sum = 0.0
        for ideom_name, required_weight in self.pattern.items():
            if ideom_name in ideom_network:
                weighted_sum += ideom_network[ideom_name].activation * required_weight
                
        self.activation = weighted_sum / total_weight
        
        if self.activation >= self.threshold:
            self.last_activated = time.time()
            self.activation_count += 1
            
        return self.activation
        
    def is_activated(self):
        """Check if this prefab is activated (above threshold)."""
        return self.activation >= self.threshold
```

```python
class PrefabManager:
    def __init__(self, ideom_network):
        self.ideom_network = ideom_network
        self.prefabs = {}  # {prefab_name: prefab}
        
    def add_prefab(self, name, pattern, category=None, threshold=0.15):
        """Add a new prefab to the system."""
        self.prefabs[name] = Prefab(name, pattern, category, threshold)
        return self.prefabs[name]
        
    def update_prefabs(self):
        """Update all prefabs based on current ideom activations."""
        for prefab in self.prefabs.values():
            prefab.compute_activation(self.ideom_network)
            
    def get_activated_prefabs(self, threshold=None):
        """Get all prefabs activated above their threshold."""
        return {name: prefab for name, prefab in self.prefabs.items() 
                if prefab.is_activated()}
                
    def create_prefab_from_activation(self, name, activated_ideoms, threshold=0.15):
        """Create a new prefab from a set of activated ideoms."""
        pattern = {ideom_name: ideom.activation 
                  for ideom_name, ideom in activated_ideoms.items()}
        return self.add_prefab(name, pattern, threshold=threshold)
```

### 4. Learning Mechanism

The Learning Mechanism adjusts ideom connections and creates new prefabs based on experience.

#### Implementation Details:

```python
class LearningMechanism:
    def __init__(self, ideom_network, prefab_manager, 
                 learning_rate=0.1, connection_threshold=0.05):
        self.ideom_network = ideom_network
        self.prefab_manager = prefab_manager
        self.learning_rate = learning_rate
        self.connection_threshold = connection_threshold
        self.experience_buffer = []  # Store recent experiences for learning
        
    def learn_from_activation(self, activated_ideoms):
        """Learn from a pattern of activated ideoms."""
        # Strengthen connections between co-activated ideoms
        ideom_names = list(activated_ideoms.keys())
        for i, name1 in enumerate(ideom_names):
            for name2 in ideom_names[i+1:]:
                # Only connect if both are sufficiently activated
                if (activated_ideoms[name1].activation > self.connection_threshold and
                    activated_ideoms[name2].activation > self.connection_threshold):
                    # Bidirectional connection strengthening
                    self.ideom_network[name1].connect(name2, self.learning_rate)
                    self.ideom_network[name2].connect(name1, self.learning_rate)
                    
    def learn_from_feedback(self, activated_ideoms, feedback_score):
        """Learn from feedback on a pattern of activated ideoms."""
        # Adjust connection strengths based on feedback
        adjustment = self.learning_rate * feedback_score
        
        ideom_names = list(activated_ideoms.keys())
        for i, name1 in enumerate(ideom_names):
            for name2 in ideom_names[i+1:]:
                # Strengthen or weaken connections based on feedback
                if name2 in self.ideom_network[name1].connections:
                    current_strength = self.ideom_network[name1].connections[name2]
                    new_strength = max(0.01, min(1.0, current_strength + adjustment))
                    self.ideom_network[name1].connections[name2] = new_strength
                    
                if name1 in self.ideom_network[name2].connections:
                    current_strength = self.ideom_network[name2].connections[name1]
                    new_strength = max(0.01, min(1.0, current_strength + adjustment))
                    self.ideom_network[name2].connections[name1] = new_strength
                    
    def create_prefab_from_experience(self, activated_ideoms, name=None):
        """Create a new prefab from a successful pattern of activated ideoms."""
        if not name:
            # Generate a name based on the most activated ideoms
            top_ideoms = sorted(activated_ideoms.items(), 
                               key=lambda x: x[1].activation, reverse=True)[:3]
            name = "_".join([ideom_name for ideom_name, _ in top_ideoms])
            
        return self.prefab_manager.create_prefab_from_activation(name, activated_ideoms)
        
    def add_to_experience_buffer(self, activated_ideoms, result, max_buffer_size=100):
        """Add an experience to the buffer for later learning."""
        self.experience_buffer.append((activated_ideoms, result))
        
        # Keep buffer at a reasonable size
        if len(self.experience_buffer) > max_buffer_size:
            self.experience_buffer.pop(0)
            
    def learn_from_buffer(self, batch_size=10):
        """Learn from a batch of experiences in the buffer."""
        if not self.experience_buffer:
            return
            
        # Select a batch of experiences
        batch_size = min(batch_size, len(self.experience_buffer))
        batch = random.sample(self.experience_buffer, batch_size)
        
        for activated_ideoms, result in batch:
            # Learn from the experience
            self.learn_from_activation(activated_ideoms)
            
            # If the result has a feedback score, learn from it
            if hasattr(result, 'feedback_score'):
                self.learn_from_feedback(activated_ideoms, result.feedback_score)
                
            # If the result was successful, consider creating a prefab
            if hasattr(result, 'success') and result.success:
                # Check if this pattern is significantly different from existing prefabs
                if self._is_novel_pattern(activated_ideoms):
                    self.create_prefab_from_experience(activated_ideoms)
                    
    def _is_novel_pattern(self, activated_ideoms, similarity_threshold=0.7):
        """Check if a pattern of activated ideoms is novel compared to existing prefabs."""
        for prefab in self.prefab_manager.prefabs.values():
            similarity = self._pattern_similarity(activated_ideoms, prefab.pattern)
            if similarity > similarity_threshold:
                return False
        return True
        
    def _pattern_similarity(self, activated_ideoms, prefab_pattern):
        """Calculate the similarity between an activation pattern and a prefab pattern."""
        # Convert activated_ideoms to a pattern format
        pattern = {name: ideom.activation for name, ideom in activated_ideoms.items()}
        
        # Find common ideoms
        common_ideoms = set(pattern.keys()) & set(prefab_pattern.keys())
        
        if not common_ideoms:
            return 0.0
            
        # Calculate similarity based on common ideoms
        similarity_sum = 0.0
        for ideom in common_ideoms:
            similarity_sum += min(pattern[ideom], prefab_pattern[ideom])
            
        # Normalize by the total number of unique ideoms
        total_ideoms = len(set(pattern.keys()) | set(prefab_pattern.keys()))
        
        return similarity_sum / total_ideoms
```

### 5. Reasoning Engine

The Reasoning Engine performs deduction, induction, and abduction based on the ideom network and prefabs.

#### Implementation Details:

```python
class ReasoningEngine:
    def __init__(self, ideom_network, prefab_manager, signal_propagator):
        self.ideom_network = ideom_network
        self.prefab_manager = prefab_manager
        self.signal_propagator = signal_propagator
        
    def reason(self, query, context=None):
        """Perform reasoning based on a query and optional context."""
        # Activate ideoms based on the query
        activated_ideoms = self._activate_from_text(query)
        
        # If context is provided, also activate ideoms from it
        if context:
            context_ideoms = self._activate_from_text(context)
            # Merge the activations
            for name, ideom in context_ideoms.items():
                if name in activated_ideoms:
                    # Boost existing activation
                    activated_ideoms[name].activate(ideom.activation * 0.5)
                else:
                    # Add with reduced activation
                    activated_ideoms[name] = ideom
                    activated_ideoms[name].activation *= 0.5
        
        # Propagate activation through the network
        self.signal_propagator.propagate()
        
        # Update prefabs based on the new activations
        self.prefab_manager.update_prefabs()
        
        # Get activated prefabs
        activated_prefabs = self.prefab_manager.get_activated_prefabs()
        
        # Determine the reasoning strategy based on activated prefabs
        if self._is_verification_query(activated_prefabs):
            return self._perform_verification(query, activated_ideoms, activated_prefabs)
        elif self._is_definition_query(activated_prefabs):
            return self._perform_definition(query, activated_ideoms, activated_prefabs)
        elif self._is_capability_query(activated_prefabs):
            return self._perform_capability_query(query, activated_ideoms, activated_prefabs)
        else:
            return self._perform_general_reasoning(query, activated_ideoms, activated_prefabs)
            
    def _activate_from_text(self, text):
        """Activate ideoms based on text input."""
        # Tokenize the text
        tokens = self._tokenize(text)
        
        # Activate ideoms for each token
        activated = {}
        for token in tokens:
            if token in self.ideom_network:
                self.ideom_network[token].activate()
                activated[token] = self.ideom_network[token]
                
        return activated
        
    def _tokenize(self, text):
        """Simple tokenization function."""
        # This would be replaced with a more sophisticated tokenizer
        return text.lower().split()
        
    def _is_verification_query(self, activated_prefabs):
        """Check if this is a verification query."""
        return "verification_query" in activated_prefabs
        
    def _is_definition_query(self, activated_prefabs):
        """Check if this is a definition query."""
        return "definition_query" in activated_prefabs
        
    def _is_capability_query(self, activated_prefabs):
        """Check if this is a capability query."""
        return "capability_query" in activated_prefabs
        
    def _perform_verification(self, query, activated_ideoms, activated_prefabs):
        """Perform verification reasoning."""
        # Extract the subject and target from the query
        subject, target = self._extract_verification_parts(query)
        
        if not subject or not target:
            return {"result": "unknown", "confidence": 0.1, 
                    "explanation": "Could not identify subject and target."}
        
        # Check if there's a direct connection
        if subject in self.ideom_network and target in self.ideom_network[subject].connections:
            strength = self.ideom_network[subject].connections[target]
            if strength > 0.5:
                return {"result": "confirmed", "confidence": strength,
                        "explanation": f"{subject} is directly connected to {target}."}
        
        # Check for indirect connections through prefabs
        for prefab_name, prefab in activated_prefabs.items():
            if subject in prefab.pattern and target in prefab.pattern:
                return {"result": "confirmed", "confidence": prefab.activation,
                        "explanation": f"{subject} and {target} are related through {prefab_name}."}
        
        # If no confirmation found, return negative result
        return {"result": "denied", "confidence": 0.7,
                "explanation": f"No significant connection found between {subject} and {target}."}
    
    def _perform_definition(self, query, activated_ideoms, activated_prefabs):
        """Perform definition reasoning."""
        # Extract the subject from the query
        subject = self._extract_definition_subject(query)
        
        if not subject:
            return {"result": "unknown", "confidence": 0.1,
                    "explanation": "Could not identify subject."}
        
        # Find all connections to the subject
        if subject in self.ideom_network:
            connections = self.ideom_network[subject].connections
            
            # Sort connections by strength
            sorted_connections = sorted(connections.items(), key=lambda x: x[1], reverse=True)
            
            # Build definition from top connections
            definition_parts = []
            for connected, strength in sorted_connections[:5]:  # Top 5 connections
                if strength > 0.3:  # Only include significant connections
                    definition_parts.append(f"{connected} ({strength:.2f})")
            
            if definition_parts:
                definition = ", ".join(definition_parts)
                return {"result": "definition", "confidence": 0.8,
                        "definition": definition,
                        "explanation": f"Definition based on strongest connections to {subject}."}
        
        # If no definition found, return unknown
        return {"result": "unknown", "confidence": 0.5,
                "explanation": f"No significant connections found for {subject}."}
    
    def _perform_capability_query(self, query, activated_ideoms, activated_prefabs):
        """Perform capability query reasoning."""
        # Extract the subject from the query
        subject = self._extract_capability_subject(query)
        
        if not subject:
            return {"result": "unknown", "confidence": 0.1,
                    "explanation": "Could not identify subject."}
        
        # Find capabilities (connections to action ideoms)
        capabilities = []
        if subject in self.ideom_network:
            for connected, strength in self.ideom_network[subject].connections.items():
                if connected in self.ideom_network and self.ideom_network[connected].category == "action":
                    if strength > 0.3:  # Only include significant capabilities
                        capabilities.append((connected, strength))
            
            # Sort by strength
            capabilities.sort(key=lambda x: x[1], reverse=True)
            
            if capabilities:
                capability_text = ", ".join([f"{cap} ({strength:.2f})" for cap, strength in capabilities[:5]])
                return {"result": "capabilities", "confidence": 0.8,
                        "capabilities": capability_text,
                        "explanation": f"Capabilities based on connections to action ideoms for {subject}."}
        
        # If no capabilities found, return unknown
        return {"result": "unknown", "confidence": 0.5,
                "explanation": f"No significant capabilities found for {subject}."}
    
    def _perform_general_reasoning(self, query, activated_ideoms, activated_prefabs):
        """Perform general reasoning when no specific query type is identified."""
        # Find the most activated ideoms and prefabs
        top_ideoms = sorted(activated_ideoms.items(), key=lambda x: x[1].activation, reverse=True)[:5]
        top_prefabs = sorted(activated_prefabs.items(), key=lambda x: x[1].activation, reverse=True)[:3]
        
        # Build a response based on the most activated elements
        response = {"result": "general", "confidence": 0.5}
        
        if top_ideoms:
            response["top_ideoms"] = [(name, ideom.activation) for name, ideom in top_ideoms]
            
        if top_prefabs:
            response["top_prefabs"] = [(name, prefab.activation) for name, prefab in top_prefabs]
            
        # Try to find connections between top ideoms
        connections = []
        for i, (name1, _) in enumerate(top_ideoms):
            for name2, _ in top_ideoms[i+1:]:
                if name1 in self.ideom_network and name2 in self.ideom_network[name1].connections:
                    connections.append((name1, name2, self.ideom_network[name1].connections[name2]))
        
        if connections:
            response["connections"] = connections
            
        return response
    
    def _extract_verification_parts(self, query):
        """Extract subject and target from a verification query."""
        # This would be replaced with a more sophisticated parser
        words = query.lower().split()
        if len(words) >= 3 and "is" in words:
            is_index = words.index("is")
            if is_index > 0 and is_index < len(words) - 1:
                subject = words[is_index - 1]
                target = words[is_index + 1]
                return subject, target
        return None, None
    
    def _extract_definition_subject(self, query):
        """Extract subject from a definition query."""
        # This would be replaced with a more sophisticated parser
        words = query.lower().split()
        if len(words) >= 3 and "what" in words and "is" in words:
            is_index = words.index("is")
            if is_index < len(words) - 1:
                return words[is_index + 1]
        return None
    
    def _extract_capability_subject(self, query):
        """Extract subject from a capability query."""
        # This would be replaced with a more sophisticated parser
        words = query.lower().split()
        if len(words) >= 3 and "what" in words and "can" in words:
            can_index = words.index("can")
            if can_index < len(words) - 1:
                return words[can_index + 1]
        return None
```

### 6. Response Generation

The Response Generation system creates natural language responses without relying on templates.

#### Implementation Details:

```python
class ResponseGenerator:
    def __init__(self, ideom_network, prefab_manager):
        self.ideom_network = ideom_network
        self.prefab_manager = prefab_manager
        
    def generate_response(self, reasoning_result, query=None):
        """Generate a natural language response based on reasoning results."""
        result_type = reasoning_result.get("result", "unknown")
        
        if result_type == "confirmed":
            return self._generate_confirmation(reasoning_result, query)
        elif result_type == "denied":
            return self._generate_denial(reasoning_result, query)
        elif result_type == "definition":
            return self._generate_definition(reasoning_result, query)
        elif result_type == "capabilities":
            return self._generate_capabilities(reasoning_result, query)
        elif result_type == "general":
            return self._generate_general_response(reasoning_result, query)
        else:
            return self._generate_unknown_response(reasoning_result, query)
    
    def _generate_confirmation(self, reasoning_result, query):
        """Generate a confirmation response."""
        confidence = reasoning_result.get("confidence", 0.5)
        explanation = reasoning_result.get("explanation", "")
        
        # Extract subject and target from the query or explanation
        subject, target = self._extract_entities_from_explanation(explanation)
        
        if confidence > 0.8:
            return f"Yes, {subject} is definitely {target}. {explanation}"
        elif confidence > 0.5:
            return f"Yes, {subject} appears to be {target}. {explanation}"
        else:
            return f"It seems that {subject} might be {target}, but I'm not entirely certain. {explanation}"
    
    def _generate_denial(self, reasoning_result, query):
        """Generate a denial response."""
        confidence = reasoning_result.get("confidence", 0.5)
        explanation = reasoning_result.get("explanation", "")
        
        # Extract subject and target from the query or explanation
        subject, target = self._extract_entities_from_explanation(explanation)
        
        if confidence > 0.8:
            return f"No, {subject} is not {target}. {explanation}"
        elif confidence > 0.5:
            return f"No, {subject} does not appear to be {target}. {explanation}"
        else:
            return f"I don't think {subject} is {target}, but I'm not entirely certain. {explanation}"
    
    def _generate_definition(self, reasoning_result, query):
        """Generate a definition response."""
        definition = reasoning_result.get("definition", "")
        explanation = reasoning_result.get("explanation", "")
        
        # Extract subject from the query or explanation
        subject = self._extract_subject_from_explanation(explanation)
        
        return f"{subject} is related to {definition}. {explanation}"
    
    def _generate_capabilities(self, reasoning_result, query):
        """Generate a capabilities response."""
        capabilities = reasoning_result.get("capabilities", "")
        explanation = reasoning_result.get("explanation", "")
        
        # Extract subject from the query or explanation
        subject = self._extract_subject_from_explanation(explanation)
        
        return f"{subject} can {capabilities}. {explanation}"
    
    def _generate_general_response(self, reasoning_result, query):
        """Generate a general response based on activated ideoms and prefabs."""
        top_ideoms = reasoning_result.get("top_ideoms", [])
        top_prefabs = reasoning_result.get("top_prefabs", [])
        connections = reasoning_result.get("connections", [])
        
        response_parts = []
        
        if top_ideoms:
            ideom_names = [name for name, _ in top_ideoms[:3]]
            response_parts.append(f"I'm thinking about {', '.join(ideom_names)}.")
            
        if top_prefabs:
            prefab_names = [name for name, _ in top_prefabs[:2]]
            response_parts.append(f"This reminds me of {', '.join(prefab_names)}.")
            
        if connections:
            connection = connections[0]  # Just use the first connection
            response_parts.append(f"I see a connection between {connection[0]} and {connection[1]}.")
            
        if not response_parts:
            response_parts.append("I'm not sure how to respond to that.")
            
        return " ".join(response_parts)
    
    def _generate_unknown_response(self, reasoning_result, query):
        """Generate a response for unknown queries."""
        explanation = reasoning_result.get("explanation", "")
        
        return f"I'm not sure about that. {explanation}"
    
    def _extract_entities_from_explanation(self, explanation):
        """Extract subject and target entities from an explanation."""
        # This would be replaced with a more sophisticated parser
        if "between" in explanation and "and" in explanation:
            between_index = explanation.index("between")
            and_index = explanation.index("and")
            if between_index < and_index:
                subject = explanation[between_index + 8:and_index].strip()
                target = explanation[and_index + 4:].strip(".")
                return subject, target
        
        # Fallback
        words = explanation.split()
        if len(words) >= 2:
            return words[0], words[-1]
        return "this", "that"
    
    def _extract_subject_from_explanation(self, explanation):
        """Extract subject from an explanation."""
        # This would be replaced with a more sophisticated parser
        if "for" in explanation:
            for_index = explanation.index("for")
            subject = explanation[for_index + 4:].strip(".")
            return subject
        
        # Fallback
        words = explanation.split()
        if words:
            return words[0]
        return "this"
```

### 7. Unified Reasoning Core

The Unified Reasoning Core integrates all these components into a cohesive system.

#### Implementation Details:

```python
class UnifiedReasoningCore:
    def __init__(self):
        # Initialize the ideom network
        self.ideom_network = {}
        
        # Initialize the components
        self.signal_propagator = SignalPropagator(self.ideom_network)
        self.prefab_manager = PrefabManager(self.ideom_network)
        self.learning_mechanism = LearningMechanism(self.ideom_network, self.prefab_manager)
        self.reasoning_engine = ReasoningEngine(self.ideom_network, self.prefab_manager, self.signal_propagator)
        self.response_generator = ResponseGenerator(self.ideom_network, self.prefab_manager)
        
        # Initialize with basic ideoms and prefabs
        self._initialize_basic_knowledge()
        
    def _initialize_basic_knowledge(self):
        """Initialize the system with basic knowledge."""
        # Add basic ideoms
        basic_ideoms = [
            ("entity", "category"),
            ("object", "category"),
            ("action", "category"),
            ("property", "category"),
            ("relation", "category"),
            ("is", "relation"),
            ("has", "relation"),
            ("can", "relation"),
            ("does", "relation"),
            ("what", "query"),
            ("who", "query"),
            ("where", "query"),
            ("when", "query"),
            ("why", "query"),
            ("how", "query")
        ]
        
        for name, category in basic_ideoms:
            self.add_ideom(name, category)
            
        # Add basic prefabs
        self.prefab_manager.add_prefab(
            "definition_query",
            {"what": 1.0, "is": 1.0},
            "query"
        )
        
        self.prefab_manager.add_prefab(
            "verification_query",
            {"is": 1.0},
            "query"
        )
        
        self.prefab_manager.add_prefab(
            "capability_query",
            {"what": 0.8, "can": 1.0},
            "query"
        )
        
    def add_ideom(self, name, category=None):
        """Add a new ideom to the network."""
        if name not in self.ideom_network:
            self.ideom_network[name] = Ideom(name, category)
        return self.ideom_network[name]
        
    def process_text(self, text, context=None):
        """Process text input and generate a response."""
        # Perform reasoning
        reasoning_result = self.reasoning_engine.reason(text, context)
        
        # Generate a response
        response = self.response_generator.generate_response(reasoning_result, text)
        
        # Learn from this interaction
        activated_ideoms = self.signal_propagator.get_activated_ideoms()
        self.learning_mechanism.learn_from_activation(activated_ideoms)