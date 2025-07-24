# IRA System Examples

This directory contains example scripts that demonstrate various features and capabilities of the IRA (Ideom Resolver AI) system.

## Overview

The example scripts in this directory are designed to showcase how different components of the IRA system work and how they can be used in practice. These scripts are intended to be educational and to provide a starting point for developers who want to use or extend the IRA system.

## Example Scripts

### Reasoning Knowledge Integration Demo

The `reasoning_knowledge_integration_demo.py` script demonstrates the integration between the Unified Reasoning Core and the Knowledge Graph, which is a critical part of the IRA system's architecture.

This script:

1. Initializes the IRA system with all its components
2. Creates several concepts in the Knowledge Graph (dog, cat, car, bicycle)
3. Adds properties and relationships to these concepts
4. Shows how the concepts in the Knowledge Graph are transformed into ideoms in the Ideom Network
5. Shows how prefabs are created in the Unified Reasoning Core based on these concepts
6. Processes several example queries to demonstrate how the integration works in practice

To run this demo, execute the following command from the project root directory:

```bash
python -m ira.examples.reasoning_knowledge_integration_demo
```

## Running the Examples

All example scripts can be run directly from the project root directory using the Python module syntax:

```bash
python -m ira.examples.<script_name_without_extension>
```

For example, to run the reasoning knowledge integration demo:

```bash
python -m ira.examples.reasoning_knowledge_integration_demo
```

## Adding New Examples

When adding new example scripts:

1. Create a new Python file in the `ira/examples` directory
2. Add a detailed docstring at the top of the file explaining what the example demonstrates
3. Include comments throughout the code to explain what each part does
4. Update this README file to document the new example

## Example Design Principles

The example scripts follow these design principles:

1. **Clarity**: Examples should be clear and easy to understand, with descriptive names and comments
2. **Completeness**: Examples should demonstrate a complete feature or capability
3. **Independence**: Each example should be self-contained and not depend on other examples
4. **Educational**: Examples should be designed to teach developers how to use the IRA system
5. **Practical**: Examples should demonstrate practical use cases for the IRA system