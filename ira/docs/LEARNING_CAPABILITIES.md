# IRA Learning Capabilities

This document describes the learning capabilities of the IRA (Ideom Resolver AI) system, which allow it to learn from various knowledge sources such as text files and Wikipedia articles.

## Overview

The IRA system now includes robust learning capabilities that enable it to expand its knowledge base dynamically. These capabilities are implemented through the following components:

1. **FileKnowledgeLoader**: Loads knowledge from text files
2. **WikipediaKnowledgeLoader**: Loads knowledge from Wikipedia articles
3. **KnowledgeLoaderManager**: Manages the knowledge loaders and provides a unified interface

These components are integrated with the IRA system's core architecture, including the Knowledge Graph, Unified Reasoning Core, and the integration between them.

## Knowledge Loaders

### FileKnowledgeLoader

The `FileKnowledgeLoader` allows the IRA system to learn from text files. It processes the file content in chunks to extract knowledge and add it to the system's knowledge graph.

Features:
- Load knowledge from text files of any size
- Process file content in manageable chunks
- Extract concepts, properties, and relations from the text
- Add the extracted knowledge to the knowledge graph
- Create ideoms and prefabs in the reasoning core based on the extracted knowledge

### WikipediaKnowledgeLoader

The `WikipediaKnowledgeLoader` allows the IRA system to learn from Wikipedia articles. It fetches articles from Wikipedia, processes their content, and adds the extracted knowledge to the system's knowledge graph.

Features:
- Search for Wikipedia articles matching a query
- Fetch Wikipedia articles by title
- Process article content in manageable chunks
- Extract concepts, properties, and relations from the article
- Add the extracted knowledge to the knowledge graph
- Create ideoms and prefabs in the reasoning core based on the extracted knowledge

### KnowledgeLoaderManager

The `KnowledgeLoaderManager` provides a centralized interface for all knowledge loaders in the IRA system. It manages the knowledge loaders and provides methods for loading knowledge from various sources.

Features:
- Unified interface for all knowledge loaders
- Methods for loading knowledge from files and Wikipedia
- Methods for searching Wikipedia articles
- Integration with the IRA system's core components

## Integration with IRA System

The learning capabilities are integrated with the IRA system through the `IRASystem` class, which provides methods for learning from various sources:

- `learn_from_file(file_path)`: Learn knowledge from a file
- `learn_from_text(text, source_name)`: Learn knowledge from a text string
- `learn_from_wikipedia(title)`: Learn knowledge from a Wikipedia article
- `learn_from_wikipedia_search(query, limit)`: Learn knowledge from Wikipedia articles matching a search query
- `search_wikipedia(query, limit)`: Search for Wikipedia articles matching a query

## Chat Interface Commands

The IRA chat interface includes commands for using the learning capabilities:

- `learn_file <file_path>`: Learn knowledge from a file
- `learn_wiki <title>`: Learn knowledge from a Wikipedia article
- `search_wiki <query>`: Search Wikipedia for articles
- `learn_wiki_search <query>`: Learn from Wikipedia articles matching a search query

## Usage Examples

### Learning from a File

```python
from ira.core.ira_system import IRASystem

# Create an IRA system
ira_system = IRASystem()

# Learn from a file
result = ira_system.learn_from_file("path/to/file.txt")

# Check the result
if result["success"]:
    print(f"Successfully learned from file. Created {len(result['concepts_created'])} concepts.")
else:
    print(f"Failed to learn from file: {result['error']}")
```

### Learning from Wikipedia

```python
from ira.core.ira_system import IRASystem

# Create an IRA system
ira_system = IRASystem()

# Search for Wikipedia articles
search_result = ira_system.search_wikipedia("Python programming language")

# Learn from the first article
if search_result["success"] and search_result["results"]:
    article_title = search_result["results"][0]["title"]
    result = ira_system.learn_from_wikipedia(article_title)
    
    if result["success"]:
        print(f"Successfully learned from Wikipedia article. Created {len(result['concepts_created'])} concepts.")
    else:
        print(f"Failed to learn from Wikipedia article: {result['error']}")
```

## Testing

The learning capabilities can be tested using the provided test scripts:

- `ira/tests/test_knowledge_loaders.py`: Unit tests for the knowledge loaders
- `ira/scripts/test_knowledge_loading.py`: Demonstration script for the knowledge loading functionality

To run the tests:

```bash
# Run the unit tests
python -m ira.tests.test_knowledge_loaders

# Run the demonstration script
python -m ira.scripts.test_knowledge_loading
```

## Future Enhancements

Planned enhancements for the learning capabilities include:

1. Support for more knowledge sources (e.g., web pages, PDFs, databases)
2. Improved knowledge extraction from unstructured text
3. Better handling of conflicting information
4. Learning from conversations and user feedback
5. Continuous learning and knowledge refinement
6. Integration with external knowledge bases and APIs