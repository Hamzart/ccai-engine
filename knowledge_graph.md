# Knowledge Graph Implementation

The Knowledge Graph is a flexible, self-organizing structure that represents knowledge in a way that can handle ambiguity and uncertainty. This document provides a detailed implementation plan for this core component.

## Core Principles

The Knowledge Graph is based on the following principles:

1. **Flexible Representation**: Knowledge is represented in a way that can handle different levels of abstraction and ambiguity.
2. **Self-Organization**: The graph can reorganize itself based on new knowledge and learning.
3. **Uncertainty Handling**: The system can represent and reason with uncertain or ambiguous knowledge.
4. **Semantic Similarity**: The graph can find related concepts based on semantic similarity.
5. **Dynamic Structure**: The structure can evolve over time as new knowledge is acquired.

## Core Components

### 1. Concept Nodes

Concept Nodes represent entities, actions, properties, and other concepts in the knowledge graph.

#### Implementation Details:

```python
class ConceptNode:
    def __init__(self, name, ctype="entity"):
        self.name = name
        self.ctype = ctype  # entity, action, property, relation, etc.
        self.aliases = []  # Alternative names for this concept
        self.properties = {}  # {property_name: [PropertyValue]}
        self.relations = {}  # {relation_type: [target_node_name]}
        self.confidence = 1.0  # Overall confidence in this concept
        self.last_updated = time.time()
        self.creation_time = time.time()
        self.access_count = 0  # How many times this node has been accessed
        self.metadata = {}  # Additional metadata
        
    def add_alias(self, alias):
        """Add an alternative name for this concept."""
        if alias not in self.aliases:
            self.aliases.append(alias)
            
    def add_property(self, property_name, value, confidence=1.0):
        """Add a property value with confidence."""
        if property_name not in self.properties:
            self.properties[property_name] = []
            
        # Check if this value already exists
        for prop in self.properties[property_name]:
            if prop.value == value:
                # Update confidence using Bayesian update
                prop.confidence = self._bayesian_update(prop.confidence, confidence)
                prop.last_updated = time.time()
                return prop
                
        # Add new property value
        prop_value = PropertyValue(value, confidence)
        self.properties[property_name].append(prop_value)
        return prop_value
        
    def add_relation(self, relation_type, target_node, confidence=1.0):
        """Add a relation to another node with confidence."""
        if relation_type not in self.relations:
            self.relations[relation_type] = []
            
        # Check if this relation already exists
        for rel in self.relations[relation_type]:
            if rel.target == target_node:
                # Update confidence using Bayesian update
                rel.confidence = self._bayesian_update(rel.confidence, confidence)
                rel.last_updated = time.time()
                return rel
                
        # Add new relation
        relation = Relation(target_node, confidence)
        self.relations[relation_type].append(relation)
        return relation
        
    def get_property(self, property_name, threshold=0.0):
        """Get property values above confidence threshold."""
        if property_name not in self.properties:
            return []
            
        return [prop for prop in self.properties[property_name] 
                if prop.confidence > threshold]
                
    def get_relations(self, relation_type=None, threshold=0.0):
        """Get relations above confidence threshold."""
        if relation_type is None:
            # Get all relations
            all_relations = []
            for rel_type, relations in self.relations.items():
                all_relations.extend([(rel_type, rel) for rel in relations 
                                     if rel.confidence > threshold])
            return all_relations
        
        if relation_type not in self.relations:
            return []
            
        return [(relation_type, rel) for rel in self.relations[relation_type] 
                if rel.confidence > threshold]
                
    def _bayesian_update(self, prior, likelihood):
        """Update confidence using Bayesian update."""
        # Simple Bayesian update formula
        posterior = (prior * likelihood) / ((prior * likelihood) + (1 - prior) * (1 - likelihood))
        return posterior
```

```python
class PropertyValue:
    def __init__(self, value, confidence=1.0):
        self.value = value
        self.confidence = confidence
        self.creation_time = time.time()
        self.last_updated = time.time()
        self.source = None  # Where this property came from
        self.metadata = {}  # Additional metadata
        
    def update(self, confidence):
        """Update confidence in this property value."""
        # Use Bayesian update
        self.confidence = (self.confidence * confidence) / ((self.confidence * confidence) + 
                                                          (1 - self.confidence) * (1 - confidence))
        self.last_updated = time.time()
```

```python
class Relation:
    def __init__(self, target, confidence=1.0):
        self.target = target  # Target node name
        self.confidence = confidence
        self.creation_time = time.time()
        self.last_updated = time.time()
        self.source = None  # Where this relation came from
        self.metadata = {}  # Additional metadata
        
    def update(self, confidence):
        """Update confidence in this relation."""
        # Use Bayesian update
        self.confidence = (self.confidence * confidence) / ((self.confidence * confidence) + 
                                                          (1 - self.confidence) * (1 - confidence))
        self.last_updated = time.time()
```

### 2. Relationship Edges

Relationship Edges represent the connections between concepts with confidence scores.

#### Implementation Details:

```python
class RelationshipType:
    def __init__(self, name, symmetric=False, transitive=False, inverse=None):
        self.name = name
        self.symmetric = symmetric  # If A relates to B, does B relate to A?
        self.transitive = transitive  # If A relates to B and B to C, does A relate to C?
        self.inverse = inverse  # Inverse relationship (e.g., "parent" -> "child")
        self.creation_time = time.time()
        self.metadata = {}  # Additional metadata
```

### 3. Uncertainty Handling

The Uncertainty Handling system represents and reasons with uncertain or ambiguous knowledge.

#### Implementation Details:

```python
class UncertaintyHandler:
    def __init__(self, graph):
        self.graph = graph
        
    def get_confidence(self, node_name, relation_type=None, target=None):
        """Get confidence in a node, relation, or specific relationship."""
        node = self.graph.get_node(node_name)
        if not node:
            return 0.0
            
        if relation_type is None and target is None:
            # Return confidence in the node itself
            return node.confidence
            
        if relation_type is not None and target is None:
            # Return average confidence in all relations of this type
            relations = node.get_relations(relation_type)
            if not relations:
                return 0.0
                
            return sum(rel.confidence for _, rel in relations) / len(relations)
            
        if relation_type is not None and target is not None:
            # Return confidence in specific relationship
            relations = node.get_relations(relation_type)
            for _, rel in relations:
                if rel.target == target:
                    return rel.confidence
                    
            return 0.0
            
    def update_confidence(self, node_name, confidence, relation_type=None, target=None):
        """Update confidence in a node, relation, or specific relationship."""
        node = self.graph.get_node(node_name)
        if not node:
            return
            
        if relation_type is None and target is None:
            # Update confidence in the node itself
            node.confidence = self._bayesian_update(node.confidence, confidence)
            return
            
        if relation_type is not None and target is None:
            # Update confidence in all relations of this type
            relations = node.get_relations(relation_type)
            for _, rel in relations:
                rel.update(confidence)
            return
            
        if relation_type is not None and target is not None:
            # Update confidence in specific relationship
            relations = node.get_relations(relation_type)
            for _, rel in relations:
                if rel.target == target:
                    rel.update(confidence)
                    return
                    
    def _bayesian_update(self, prior, likelihood):
        """Update confidence using Bayesian update."""
        # Simple Bayesian update formula
        posterior = (prior * likelihood) / ((prior * likelihood) + (1 - prior) * (1 - likelihood))
        return posterior
        
    def resolve_ambiguity(self, node_name, property_name):
        """Resolve ambiguity in property values."""
        node = self.graph.get_node(node_name)
        if not node or property_name not in node.properties:
            return None
            
        # Get property values sorted by confidence
        properties = sorted(node.properties[property_name], 
                           key=lambda x: x.confidence, reverse=True)
                           
        if not properties:
            return None
            
        # If one value is significantly more confident than others, return it
        if len(properties) == 1 or properties[0].confidence > properties[1].confidence * 1.5:
            return properties[0].value
            
        # Otherwise, return the top values with their confidences
        return [(prop.value, prop.confidence) for prop in properties[:3]]
```

### 4. Semantic Similarity

The Semantic Similarity system finds related concepts based on semantic similarity.

#### Implementation Details:

```python
class SemanticSimilarity:
    def __init__(self, graph):
        self.graph = graph
        
    def find_similar_concepts(self, concept_name, threshold=0.5, max_results=10):
        """Find concepts similar to the given concept."""
        concept = self.graph.get_node(concept_name)
        if not concept:
            return []
            
        # Calculate similarity scores for all nodes
        similarities = []
        for node_name, node in self.graph.nodes.items():
            if node_name == concept_name:
                continue
                
            similarity = self.calculate_similarity(concept, node)
            if similarity >= threshold:
                similarities.append((node_name, similarity))
                
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]
        
    def calculate_similarity(self, node1, node2):
        """Calculate semantic similarity between two nodes."""
        # Start with a base similarity
        similarity = 0.0
        
        # Check for shared properties
        shared_properties = set(node1.properties.keys()) & set(node2.properties.keys())
        if shared_properties:
            property_similarity = 0.0
            for prop in shared_properties:
                # Get values for this property
                values1 = [p.value for p in node1.properties[prop]]
                values2 = [p.value for p in node2.properties[prop]]
                
                # Calculate Jaccard similarity for property values
                intersection = set(values1) & set(values2)
                union = set(values1) | set(values2)
                
                if union:
                    property_similarity += len(intersection) / len(union)
                    
            # Normalize by number of shared properties
            property_similarity /= len(shared_properties)
            similarity += property_similarity * 0.4  # Properties contribute 40%
            
        # Check for shared relations
        shared_relations = set(node1.relations.keys()) & set(node2.relations.keys())
        if shared_relations:
            relation_similarity = 0.0
            for rel in shared_relations:
                # Get targets for this relation
                targets1 = [r.target for r in node1.relations[rel]]
                targets2 = [r.target for r in node2.relations[rel]]
                
                # Calculate Jaccard similarity for relation targets
                intersection = set(targets1) & set(targets2)
                union = set(targets1) | set(targets2)
                
                if union:
                    relation_similarity += len(intersection) / len(union)
                    
            # Normalize by number of shared relations
            relation_similarity /= len(shared_relations)
            similarity += relation_similarity * 0.6  # Relations contribute 60%
            
        return similarity
        
    def find_path(self, source, target, max_depth=3):
        """Find a path between two concepts."""
        if source == target:
            return [source]
            
        # Breadth-first search
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            (node, path) = queue.pop(0)
            
            # Stop if we've reached max depth
            if len(path) > max_depth:
                continue
                
            # Get all relations from this node
            node_obj = self.graph.get_node(node)
            if not node_obj:
                continue
                
            for rel_type, relations in node_obj.relations.items():
                for rel in relations:
                    if rel.target not in visited:
                        if rel.target == target:
                            return path + [rel.target]
                            
                        visited.add(rel.target)
                        queue.append((rel.target, path + [rel.target]))
                        
        # No path found
        return None
```

### 5. Self-Organizing Structure

The Self-Organizing Structure can reorganize itself based on new knowledge and learning.

#### Implementation Details:

```python
class SelfOrganizingStructure:
    def __init__(self, graph):
        self.graph = graph
        
    def reorganize(self):
        """Reorganize the graph based on usage patterns and relationships."""
        # Identify clusters of related concepts
        clusters = self._identify_clusters()
        
        # Strengthen connections within clusters
        for cluster in clusters:
            self._strengthen_cluster(cluster)
            
        # Identify and create higher-level concepts
        self._create_higher_level_concepts(clusters)
        
        # Prune rarely used or low-confidence nodes and relations
        self._prune_graph()
        
    def _identify_clusters(self, min_similarity=0.6):
        """Identify clusters of related concepts."""
        # Start with each node in its own cluster
        clusters = [{node} for node in self.graph.nodes.keys()]
        
        # Semantic similarity calculator
        similarity = SemanticSimilarity(self.graph)
        
        # Merge clusters that have similar concepts
        merged = True
        while merged:
            merged = False
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # Check if these clusters should be merged
                    if self._should_merge_clusters(clusters[i], clusters[j], similarity, min_similarity):
                        # Merge clusters
                        clusters[i] = clusters[i].union(clusters[j])
                        clusters.pop(j)
                        merged = True
                        break
                if merged:
                    break
                    
        return clusters
        
    def _should_merge_clusters(self, cluster1, cluster2, similarity, threshold):
        """Determine if two clusters should be merged."""
        # Calculate average similarity between concepts in the clusters
        total_similarity = 0.0
        comparisons = 0
        
        for concept1 in cluster1:
            node1 = self.graph.get_node(concept1)
            if not node1:
                continue
                
            for concept2 in cluster2:
                node2 = self.graph.get_node(concept2)
                if not node2:
                    continue
                    
                total_similarity += similarity.calculate_similarity(node1, node2)
                comparisons += 1
                
        if comparisons == 0:
            return False
            
        avg_similarity = total_similarity / comparisons
        return avg_similarity >= threshold
        
    def _strengthen_cluster(self, cluster):
        """Strengthen connections within a cluster."""
        # For each pair of concepts in the cluster
        for concept1 in cluster:
            node1 = self.graph.get_node(concept1)
            if not node1:
                continue
                
            for concept2 in cluster:
                if concept1 == concept2:
                    continue
                    
                node2 = self.graph.get_node(concept2)
                if not node2:
                    continue
                    
                # Add or strengthen "related_to" relation
                relation = node1.add_relation("related_to", concept2, 0.7)
                relation.update(0.7)  # Strengthen the connection
                
    def _create_higher_level_concepts(self, clusters, min_size=3):
        """Create higher-level concepts for large clusters."""
        for i, cluster in enumerate(clusters):
            if len(cluster) >= min_size:
                # Create a higher-level concept
                cluster_name = f"cluster_{i}"
                
                # Try to find a meaningful name based on common properties
                common_name = self._find_common_name(cluster)
                if common_name:
                    cluster_name = common_name
                    
                # Create the cluster node if it doesn't exist
                if not self.graph.get_node(cluster_name):
                    self.graph.add_node(cluster_name, "category")
                    
                # Connect cluster members to the cluster
                for concept in cluster:
                    node = self.graph.get_node(concept)
                    if node:
                        # Add "is_a" relation to the cluster
                        node.add_relation("is_a", cluster_name, 0.8)
                        
                        # Add "has_member" relation from cluster to member
                        cluster_node = self.graph.get_node(cluster_name)
                        cluster_node.add_relation("has_member", concept, 0.8)
                        
    def _find_common_name(self, cluster):
        """Find a common name for a cluster based on shared properties."""
        # Get all nodes in the cluster
        nodes = [self.graph.get_node(concept) for concept in cluster if self.graph.get_node(concept)]
        
        if not nodes:
            return None
            
        # Find common "is_a" relations
        common_categories = None
        for node in nodes:
            categories = {rel.target for rel in node.get_relations("is_a")}
            if common_categories is None:
                common_categories = categories
            else:
                common_categories &= categories
                
        if common_categories and len(common_categories) > 0:
            # Use the first common category as the cluster name
            return next(iter(common_categories))
            
        return None
        
    def _prune_graph(self, min_confidence=0.2, min_access_count=1):
        """Prune rarely used or low-confidence nodes and relations."""
        # Identify nodes to prune
        nodes_to_prune = []
        for node_name, node in self.graph.nodes.items():
            if node.confidence < min_confidence and node.access_count <= min_access_count:
                nodes_to_prune.append(node_name)
                
        # Prune nodes
        for node_name in nodes_to_prune:
            self.graph.remove_node(node_name)
            
        # Prune low-confidence relations
        for node_name, node in self.graph.nodes.items():
            for rel_type in list(node.relations.keys()):
                # Filter out low-confidence relations
                node.relations[rel_type] = [rel for rel in node.relations[rel_type] 
                                          if rel.confidence >= min_confidence]
                
                # Remove empty relation types
                if not node.relations[rel_type]:
                    del node.relations[rel_type]
```

### 6. Knowledge Graph

The Knowledge Graph integrates all these components into a cohesive system.

#### Implementation Details:

```python
class KnowledgeGraph:
    def __init__(self, storage_path=None):
        self.nodes = {}  # {node_name: ConceptNode}
        self.relation_types = {}  # {relation_name: RelationshipType}
        self.storage_path = storage_path
        
        # Initialize components
        self.uncertainty_handler = UncertaintyHandler(self)
        self.semantic_similarity = SemanticSimilarity(self)
        self.self_organizing = SelfOrganizingStructure(self)
        
        # Initialize with basic relation types
        self._initialize_relation_types()
        
    def _initialize_relation_types(self):
        """Initialize basic relation types."""
        # Add basic relation types
        self.add_relation_type("is_a", transitive=True)
        self.add_relation_type("has_part", inverse="part_of")
        self.add_relation_type("part_of", inverse="has_part")
        self.add_relation_type("related_to", symmetric=True)
        self.add_relation_type("can_do")
        self.add_relation_type("has_property")
        self.add_relation_type("has_member", inverse="member_of")
        self.add_relation_type("member_of", inverse="has_member")
        
    def add_node(self, name, ctype="entity"):
        """Add a new node to the graph."""
        if name in self.nodes:
            return self.nodes[name]
            
        node = ConceptNode(name, ctype)
        self.nodes[name] = node
        return node
        
    def get_node(self, name):
        """Get a node by name or alias."""
        if name in self.nodes:
            # Update access count
            self.nodes[name].access_count += 1
            return self.nodes[name]
            
        # Check aliases
        for node_name, node in self.nodes.items():
            if name in node.aliases:
                # Update access count
                node.access_count += 1
                return node
                
        return None
        
    def remove_node(self, name):
        """Remove a node from the graph."""
        if name in self.nodes:
            # Remove all relations to this node
            for node_name, node in self.nodes.items():
                for rel_type in list(node.relations.keys()):
                    node.relations[rel_type] = [rel for rel in node.relations[rel_type] 
                                              if rel.target != name]
                    
                    # Remove empty relation types
                    if not node.relations[rel_type]:
                        del node.relations[rel_type]
                        
            # Remove the node
            del self.nodes[name]
            
    def add_relation_type(self, name, symmetric=False, transitive=False, inverse=None):
        """Add a new relation type."""
        if name in self.relation_types:
            return self.relation_types[name]
            
        rel_type = RelationshipType(name, symmetric, transitive, inverse)
        self.relation_types[name] = rel_type
        
        # Add inverse relation type if specified
        if inverse and inverse not in self.relation_types:
            inverse_rel = RelationshipType(inverse, symmetric, transitive, name)
            self.relation_types[inverse] = inverse_rel
            
        return rel_type
        
    def add_relation(self, source, relation_type, target, confidence=1.0):
        """Add a relation between two nodes."""
        # Get or create nodes
        source_node = self.get_node(source)
        if not source_node:
            source_node = self.add_node(source)
            
        target_node = self.get_node(target)
        if not target_node:
            target_node = self.add_node(target)
            
        # Add the relation
        relation = source_node.add_relation(relation_type, target, confidence)
        
        # If the relation type is symmetric, add the inverse relation
        rel_type = self.relation_types.get(relation_type)
        if rel_type and rel_type.symmetric:
            target_node.add_relation(relation_type, source, confidence)
            
        # If the relation type has an inverse, add the inverse relation
        if rel_type and rel_type.inverse:
            target_node.add_relation(rel_type.inverse, source, confidence)
            
        return relation
        
    def add_property(self, node_name, property_name, value, confidence=1.0):
        """Add a property to a node."""
        node = self.get_node(node_name)
        if not node:
            node = self.add_node(node_name)
            
        return node.add_property(property_name, value, confidence)
        
    def query(self, query_type, params):
        """Query the knowledge graph."""
        if query_type == "get_node":
            return self.get_node(params["name"])
            
        elif query_type == "get_relations":
            node = self.get_node(params["name"])
            if not node:
                return []
                
            return node.get_relations(params.get("relation_type"), params.get("threshold", 0.0))
            
        elif query_type == "get_property":
            node = self.get_node(params["name"])
            if not node:
                return []
                
            return node.get_property(params["property_name"], params.get("threshold", 0.0))
            
        elif query_type == "find_similar":
            return self.semantic_similarity.find_similar_concepts(
                params["name"], 
                params.get("threshold", 0.5),
                params.get("max_results", 10)
            )
            
        elif query_type == "find_path":
            return self.semantic_similarity.find_path(
                params["source"],
                params["target"],
                params.get("max_depth", 3)
            )
            
        return None
        
    def learn(self, knowledge):
        """Learn from new knowledge."""
        if isinstance(knowledge, list):
            # Process a list of knowledge items
            for item in knowledge:
                self._process_knowledge_item(item)
        else:
            # Process a single knowledge item
            self._process_knowledge_item(knowledge)
            
        # Periodically reorganize the graph
        if random.random() < 0.1:  # 10% chance
            self.self_organizing.reorganize()
            
    def _process_knowledge_item(self, item):
        """Process a single knowledge item."""
        if "subject" in item and "relation" in item and "object" in item:
            # Process a triplet
            confidence = item.get("confidence", 1.0)
            
            if item["relation"] == "is_a":
                # Add is_a relation
                self.add_relation(item["subject"], "is_a", item["object"], confidence)
                
            elif item["relation"] == "has_part":
                # Add has_part relation
                self.add_relation(item["subject"], "has_part", item["object"], confidence)
                
            elif item["relation"] == "can_do":
                # Add can_do relation
                self.add_relation(item["subject"], "can_do", item["object"], confidence)
                
            elif item["relation"] == "has_property":
                # Add property
                self.add_property(item["subject"], "property", item["object"], confidence)
                
            else:
                # Add generic relation
                self.add_relation(item["subject"], item["relation"], item["object"], confidence)
                
        elif "entity" in item and "properties" in item:
            # Process entity with properties
            entity = item["entity"]
            
            # Add the entity
            node = self.add_node(entity, item.get("type", "entity"))
            
            # Add properties
            for prop_name, prop_value in item["properties"].items():
                confidence = 1.0
                if isinstance(prop_value, dict):
                    confidence = prop_value.get("confidence", 1.0)
                    prop_value = prop_value["value"]
                    
                self.add_property(entity, prop_name, prop_value, confidence)
                
        elif "entity" in item and "relations" in item:
            # Process entity with relations
            entity = item["entity"]
            
            # Add the entity
            node = self.add_node(entity, item.get("type", "entity"))
            
            # Add relations
            for rel_type, targets in item["relations"].items():
                for target in targets:
                    confidence = 1.0
                    if isinstance(target, dict):
                        confidence = target.get("confidence", 1.0)
                        target = target["target"]
                        
                    self.add_relation(entity, rel_type, target, confidence)
                    
    def save(self):
        """Save the knowledge graph to disk."""
        if not self.storage_path:
            return
            
        # Create directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save nodes
        with open(os.path.join(self.storage_path, "nodes.pkl"), "wb") as f:
            pickle.dump(self.nodes, f)
            
        # Save relation types
        with open(os.path.join(self.storage_path, "relation_types.pkl"), "wb") as f:
            pickle.dump(self.relation_types, f)
            
    def load(self):
        """Load the knowledge graph from disk."""
        if not self.storage_path:
            return
            
        # Load nodes
        nodes_path = os.path.join(self.storage_path, "nodes.pkl")
        if os.path.exists(nodes_path):
            with open(nodes_path, "rb") as f:
                self.nodes = pickle.load(f)
                
        # Load relation types
        rel_types_path = os.path.join(self.storage_path, "relation_types.pkl")
        if os.path.exists(rel_types_path):
            with open(rel_types_path, "rb") as f:
                self.relation_types = pickle.load(f)
                
        # Reinitialize components
        self.uncertainty_handler = UncertaintyHandler(self)
        self.semantic_similarity = SemanticSimilarity(self)
        self.self_organizing = SelfOrganizingStructure(self)
```

## Integration with Unified Reasoning Core

The Knowledge Graph integrates with the Unified Reasoning Core through a simple interface:

```python
class KnowledgeInterface:
    def __init__(self, knowledge_graph):
        self.graph = knowledge_graph
        
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
                
                if activation1 > 0.