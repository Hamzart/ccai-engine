# Integration Components

This directory contains the integration components for the IRA (Ideom Resolver AI) system. These components connect different parts of the system, enabling them to work together seamlessly.

## Overview

The integration components are responsible for connecting the different parts of the IRA system, such as the Knowledge Graph, the Unified Reasoning Core, and the Conversation Manager. They enable these components to share information and work together to provide a coherent and intelligent response to user input.

## Components

### ReasoningKnowledgeIntegration

The `ReasoningKnowledgeIntegration` class integrates the Unified Reasoning Core with the Knowledge Graph. It enables the Unified Reasoning Core to access knowledge stored in the Knowledge Graph and to update the Knowledge Graph based on reasoning results.

Key features:
- Create ideoms in the Unified Reasoning Core based on concepts in the Knowledge Graph
- Create prefabs in the Unified Reasoning Core based on concepts in the Knowledge Graph
- Query the Knowledge Graph based on reasoning results
- Update the Knowledge Graph based on reasoning results
- Extract knowledge from reasoning results

### ConversationKnowledgeIntegration

The `ConversationKnowledgeIntegration` class integrates the Conversation Manager with the Knowledge Graph. It enables the Conversation Manager to access knowledge stored in the Knowledge Graph and to update the Knowledge Graph based on conversation context.

Key features:
- Query the Knowledge Graph based on conversation context
- Update the Knowledge Graph based on conversation context
- Extract knowledge from conversation context

## Bug Fixes

The `ReasoningKnowledgeIntegrationBugFixes` class provides bug fixes for the `ReasoningKnowledgeIntegration` class. These fixes address issues with multi-word concept handling, natural response templates, triple extraction, error handling, and multi-word concept querying.

To apply the bug fixes, use the `apply_bug_fixes` function:

```python
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes

# Create a ReasoningKnowledgeIntegration instance
integration = ReasoningKnowledgeIntegration(knowledge_graph, reasoning_core)

# Apply the bug fixes
apply_bug_fixes(integration)
```

For more information about the bug fixes, see the [bug fixes documentation](../../docs/reasoning_knowledge_integration_bugfixes.md).

## Usage

### Creating an Integration

To create an integration between the Unified Reasoning Core and the Knowledge Graph:

```python
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes

# Create a Knowledge Graph
knowledge_graph = KnowledgeGraph()

# Add some concepts to the Knowledge Graph
dog_concept = knowledge_graph.add_concept("dog")
knowledge_graph.update_concept(
    dog_concept.id,
    properties={
        "type": "animal",
        "legs": "four",
        "sound": "bark"
    }
)

# Create an Ideom Network
ideom_network = IdeomNetwork()

# Create a Unified Reasoning Core
reasoning_core = UnifiedReasoningCore(ideom_network=ideom_network)

# Create a Reasoning Knowledge Integration
integration = ReasoningKnowledgeIntegration(knowledge_graph, reasoning_core)

# Apply bug fixes
apply_bug_fixes(integration)

# Initialize the integration
integration.create_ideoms_from_concepts()
integration.create_prefabs_from_concepts()
```

### Processing Input with Knowledge

To process input using both the Unified Reasoning Core and the Knowledge Graph:

```python
# Process input with knowledge
result = integration.process_input_with_knowledge("What is a dog?")

# Get the primary response
response = result["reasoning_result"]["primary_response"]
print(f"Response: {response}")
```

### Querying the Knowledge Graph

To query the Knowledge Graph based on a reasoning result:

```python
# Process input with the Unified Reasoning Core
reasoning_result = reasoning_core.process("What is a dog?")

# Query the Knowledge Graph based on the reasoning result
knowledge_query_result = integration.query_knowledge_graph(reasoning_result)

# Print the query results
print(f"Query results: {knowledge_query_result['results']}")
```

### Updating the Knowledge Graph

To update the Knowledge Graph based on a reasoning result:

```python
# Process input with the Unified Reasoning Core
reasoning_result = reasoning_core.process("Dogs are loyal companions.")

# Update the Knowledge Graph based on the reasoning result
knowledge_update_result = integration.update_knowledge_graph(reasoning_result)

# Print the update results
print(f"Update results: {knowledge_update_result}")
```

### Extracting Knowledge from Reasoning

To extract knowledge from a reasoning result:

```python
# Process input with the Unified Reasoning Core
reasoning_result = reasoning_core.process("Dogs are mammals that bark.")

# Extract knowledge from the reasoning result
knowledge_extraction_result = integration.extract_knowledge_from_reasoning(reasoning_result)

# Print the extracted knowledge
print(f"Extracted knowledge: {knowledge_extraction_result['extracted_knowledge']}")
```

## Examples

For more examples of how to use the integration components, see the [examples directory](../../examples/).

- [Reasoning Knowledge Integration Demo](../../examples/reasoning_knowledge_integration_demo.py): Demonstrates how to use the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.

## Testing

The integration components are tested using the following test files:

- [test_reasoning_knowledge_integration.py](../../tests/test_reasoning_knowledge_integration.py): Tests the basic integration between the Unified Reasoning Core and the Knowledge Graph.
- [test_enhanced_reasoning_knowledge_integration.py](../../tests/test_enhanced_reasoning_knowledge_integration.py): Tests the enhanced integration with bug fixes and improvements.

To run the tests:

```bash
python -m unittest ira.tests.test_reasoning_knowledge_integration
python -m unittest ira.tests.test_enhanced_reasoning_knowledge_integration
```

## Documentation

For more information about the integration components, see the following documentation:

- [Reasoning Knowledge Integration Bug Fixes](../../docs/reasoning_knowledge_integration_bugfixes.md): Describes the bugs that were fixed in the `ReasoningKnowledgeIntegration` class.