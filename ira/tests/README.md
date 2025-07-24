# IRA System Integration Tests

This directory contains integration tests for the IRA (Ideom Resolver AI) system, focusing on testing the integration between different components of the system.

## Overview

The integration tests verify that different components of the IRA system work together correctly. Currently, the tests focus on the integration between the Unified Reasoning Core and the Knowledge Graph, which is a critical part of the IRA system's architecture.

## Test Files

- `test_reasoning_knowledge_integration.py`: Tests the integration between the Unified Reasoning Core and the Knowledge Graph.
- `run_integration_tests.py`: Script to run all integration tests.

## Running the Tests

To run all integration tests, execute the following command from the project root directory:

```bash
python -m ira.tests.run_integration_tests
```

This will run all the integration tests and display the results.

## Test Coverage

### Reasoning Knowledge Integration Tests

The `test_reasoning_knowledge_integration.py` file contains tests for the integration between the Unified Reasoning Core and the Knowledge Graph. These tests verify that:

1. **Ideom Creation**: Ideoms are correctly created in the Ideom Network based on concepts in the Knowledge Graph.
2. **Prefab Creation**: Prefabs are correctly created in the Unified Reasoning Core based on concepts in the Knowledge Graph.
3. **Input Processing**: The integration correctly processes input with knowledge from the Knowledge Graph.
4. **IRA System Integration**: The integration works correctly within the IRA system.

## Demo Script

In addition to the tests, there is a demonstration script in the `ira/examples` directory that shows the integration in action:

- `reasoning_knowledge_integration_demo.py`: Demonstrates how the integration between the Unified Reasoning Core and the Knowledge Graph works in practice.

To run the demo script, execute the following command from the project root directory:

```bash
python -m ira.examples.reasoning_knowledge_integration_demo
```

This will create some concepts in the Knowledge Graph, show how they are transformed into ideoms and prefabs in the Unified Reasoning Core, and demonstrate how they are used to process queries.

## Adding New Tests

When adding new integration tests:

1. Create a new test file in the `ira/tests` directory.
2. Add the test class to the `run_integration_tests.py` script.
3. Update this README file to document the new tests.

## Test Design Principles

The integration tests follow these design principles:

1. **Isolation**: Each test should be isolated from other tests and should not depend on the state of the system from previous tests.
2. **Completeness**: Tests should cover all aspects of the integration between components.
3. **Clarity**: Tests should be clear and easy to understand, with descriptive names and comments.
4. **Robustness**: Tests should be robust and should not fail due to minor changes in the system.