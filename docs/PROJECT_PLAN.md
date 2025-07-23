# Project Plan

This document outlines the next development steps for advancing the
Cognitive Concept AI (CCAI) engine towards a robust prototype.

## 1. Graph & Persistence Layer
- Implement asynchronous WAL writing so reasoning is never blocked by disk I/O.
- Expand `ConceptNode` with additional metadata fields such as `last_updated` and usage counters.
- Create `ConceptGraph` helper methods for updating property statistics and edges safely.

## 2. Reasoning Engine
- Add a priority based `SignalHub` to manage propagation order.
- Implement the following subsystems:
  - **FuzzyMatch** – computes similarity between property values and adjusts
    signal confidence accordingly.
  - **BayesianUpdater** – updates belief scores using priors on nodes whenever
    an observation signal is processed.
  - **ConflictResolver** – detects contradictory assertions and issues
    objection signals.
- Extend `ReasoningCore` to halt processing when signal confidence drops below
  a threshold or the queue becomes empty.

## 3. NLP & Knowledge Acquisition
- Configure spaCy pipeline loading in `InformationExtractor` and `QueryParser`.
- Develop additional extraction rules for agent–action–object phrases and for
  capturing purpose relations ("used for").
- Build a small suite of unit tests ensuring that text ingestion creates the
  expected nodes and relations.

## 4. Tooling and Documentation
- Fix the CLI initialisation bug (missing `PrimitiveManager`).
- Provide examples in the README demonstrating learning and querying.
- Expand documentation with usage guides and API references as modules
  stabilise.

### Progress
- Async WAL writer implemented via background thread.
- Added `last_updated` metadata and safe property helpers in `ConceptGraph`.
- Introduced `SignalHub` and three new reasoning subsystems.
- CLI now correctly initialises `PrimitiveManager`.

These items are intended as a starting point and can be tackled in parallel
across the three main workstreams.
