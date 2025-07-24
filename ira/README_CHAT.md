# IRA Chat Interface

This document provides instructions for using the IRA (Ideom Resolver AI) chat interface. The chat interface allows you to interact with the IRA system, which is based on the integration of a Unified Reasoning Core and a Knowledge Graph.

## Overview

The IRA system is an intelligent system based on the IRA (Ideom Resolver AI) philosophy. It uses a network of ideoms (atomic units of cognition) to represent knowledge and reason about it. The system integrates a Unified Reasoning Core, which handles the reasoning process, with a Knowledge Graph, which stores structured knowledge.

The chat interface provides a simple command-line interface for interacting with the IRA system. You can ask questions, make statements, and teach the system new things.

## Features

- **Natural Language Understanding**: The system can understand natural language input and extract meaning from it.
- **Knowledge-Based Reasoning**: The system can reason about knowledge stored in the Knowledge Graph.
- **Dynamic Response Generation**: The system can generate responses without relying on templates.
- **Learning from Feedback**: The system can learn from feedback and improve over time.
- **Temporal Context Awareness**: The system maintains a history of activation patterns over time, allowing it to track changes in activation and identify temporal patterns.
- **Multi-Word Concept Handling**: The system can handle multi-word concepts like "golden retriever".
- **Error Handling**: The system handles errors gracefully and provides helpful error messages.

## Installation

The chat interface requires Python 3.6 or later and the following packages:
- colorama
- nltk

You can install the required packages using pip:

```bash
pip install colorama nltk
```

The chat interface will automatically download the required NLTK data (punkt, stopwords, and wordnet) when it's first run. If you want to download them manually, you can use the following commands:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### NLTK Dependency Note

If you encounter any issues with NLTK dependencies, make sure all required NLTK data packages are properly installed. The system explicitly checks for and downloads the following NLTK packages:

- `punkt`: Used for tokenizing text into words and sentences
- `punkt_tab`: Used internally by the punkt tokenizer
- `stopwords`: Used for filtering out common words
- `wordnet`: Used for semantic understanding and lemmatization

If you encounter errors related to `punkt_tab` or other NLTK resources, you can manually download these packages using the NLTK downloader:

```python
import nltk
nltk.download('punkt')  # This also downloads punkt_tab
nltk.download('stopwords')
nltk.download('wordnet')
```

Or use the NLTK downloader GUI:

```python
import nltk
nltk.download()  # This will open the NLTK downloader GUI
```

Or download them directly from the command line:

```bash
python -m nltk.downloader punkt stopwords wordnet
```

Note that downloading `punkt` should also download `punkt_tab`, as they are part of the same package. If you still encounter issues with `punkt_tab`, try downloading the entire `all` package:

```python
import nltk
nltk.download('all')  # Downloads all NLTK data packages (large download)
```

## Usage

To start the chat interface, run the following command from the project root directory:

```bash
python ira/chat_interface.py
```

This will initialize the IRA system and start the chat interface. You can then interact with the system by typing messages and pressing Enter.

### Commands

The chat interface supports the following commands:

- `help`: Show a help message with available commands and example questions.
- `exit` or `quit`: Exit the chat interface.
- `clear`: Clear the screen.
- `history`: Show the conversation history.
- `save [filename]`: Save the conversation history to a file. If no filename is provided, it will be saved to `ira_conversation.txt`.

### Example Interactions

Here are some example interactions with the IRA system:

#### Asking Questions

```
You: What is a dog?
IRA: A dog is a domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking, howling, or whining voice.

You: What sound does a cat make?
IRA: A cat makes a meow sound.

You: What is a golden retriever?
IRA: A golden retriever is a medium-large gun dog that was bred to retrieve shot waterfowl, such as ducks and upland game birds, during hunting and shooting parties. It has a golden coat and a friendly temperament.
```

#### Making Statements

```
You: Dogs are loyal companions.
IRA: I've learned that dogs are loyal companions.

You: Python is a popular programming language.
IRA: I've learned that Python is a popular programming language.
```

#### Multi-Turn Conversations

```
You: Tell me about animals.
IRA: Animals are living organisms that feed on organic matter, typically having specialized sense organs and nervous system and able to respond rapidly to stimuli.

You: Which ones have four legs?
IRA: Dogs and cats have four legs.
```

## Knowledge Base

The chat interface initializes the IRA system with a small knowledge base containing information about:

- Animals (dogs, cats, birds)
- Dog breeds (golden retriever)
- Computers and programming

You can teach the system new things by making statements, and it will learn from your input.

## Customization

You can customize the knowledge base by modifying the `create_test_knowledge_graph` function in the `chat_interface.py` file. This function creates the initial Knowledge Graph with some test concepts.

## Example Scripts

The IRA system comes with several example scripts that demonstrate how to use the system:

### Simple Integration Demo

The `ira/examples/simple_integration_demo.py` script provides a minimal example of how to use the enhanced integration between the Unified Reasoning Core and the Knowledge Graph with the bug fixes applied. It demonstrates:

- Creating a simple knowledge graph
- Applying the bug fixes
- Handling basic queries
- Multi-word concept handling
- Error handling

To run the simple integration demo:

```bash
python ira/examples/simple_integration_demo.py
```

### Comprehensive Integration Demo

The `ira/examples/reasoning_knowledge_integration_demo.py` script provides a more comprehensive demonstration of the enhanced integration, including:

- Semantic understanding
- Multi-turn conversation
- Knowledge extraction
- Learning from feedback

To run the comprehensive integration demo:

```bash
python ira/examples/reasoning_knowledge_integration_demo.py
```

## Troubleshooting

If you encounter any issues with the chat interface, try the following:

1. Make sure you have installed all the required packages.
2. Make sure you are running the script from the project root directory.
3. Check the console output for any error messages.
4. Run the verification script to check if all components are working correctly:

```bash
python ira/scripts/apply_all_fixes_and_verify.py
```

This script will:
- Apply all bug fixes to the ReasoningKnowledgeIntegration class
- Run the tests to verify that the bugs have been fixed
- Verify that the chat interface works correctly
- Run the simple integration demo

If the script reports any errors, it will provide detailed information about what went wrong.

If you still have issues, please report them by creating an issue in the project repository.

## Contributing

Contributions to the IRA system and chat interface are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.