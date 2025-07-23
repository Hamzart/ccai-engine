# Cognitive Concept AI Engine

The goal of this project is to build a deterministic reasoning system that
operates through signal propagation over a knowledge graph.  Concepts are
explicitly modelled and every inference step is traceable.  The project is
currently a prototype but it already contains the core building blocks of the
``Semantic Signal‑Based AI" (SSBAI) architecture.

## Repository layout

```
ccai/                Python package with the engine
  core/              concept graph, models and reasoning subsystems
  io/                persistence helpers (snapshot & write‑ahead log)
  nlp/               text parser and information extractor
  cli/               Typer based utilities
  run.py             interactive command line demo
graph_data/          saved snapshot and WAL
knowledge.txt        seed knowledge in a simple text form
primitives.json      primitive property definitions
```

## Architecture overview

The engine follows three main workstreams:

1. **Graph & Persistence Layer** – `ConceptGraph` stores all `ConceptNode` objects
   in memory and persists them using msgpack snapshots plus a WAL in NDJSON
   format.  `GraphPersistence` handles atomic writes and replaying mutations at
   startup.
2. **Reasoning Engine** – the `ReasoningCore` dispatches `Signal` objects to a
   set of pluggable subsystems.  Current subsystems handle inheritance and
   relation lookup.  Future work will introduce fuzzy matching, Bayesian
   updates and contradiction resolution.
3. **NLP & Knowledge Acquisition** – spaCy is used for parsing text.  The
   `InformationExtractor` converts dependency parses into concept nodes and
   relations while `QueryParser` turns user questions into signals.

The full vision includes an expandable ontology, probabilistic reasoning via
Bayesian updates, conflict detection and rich natural language ingestion using a
set of heuristic extraction rules.

## Running the demo

Install the package in editable mode and download the small spaCy model first:

```bash
pip install -e .
python -m spacy download en_core_web_sm
```

Then run the interactive demo via `python -m ccai.run` and chat with the bot.
On the first launch the engine will automatically ingest `knowledge.txt` to
seed the concept graph. Use commands such as `@learn <sentence>` or
`@ingest <file>` to teach new facts.  All data is stored in `graph_data/`.
=======
Use commands such as `@learn <sentence>` or `@ingest <file>` to teach new
facts.  All data is stored in `graph_data/`.

Developers can also run `python -m ccai.cli --help` for maintenance commands.

### Example session

```bash
$ python -m ccai.run
🤖 Initializing AI...
🧠 Loading Concept Graph from disk...
✅ AI Ready. Let's chat!
You> @learn The knife is sharp.
You> What is a knife?
- tool
```

## Further information

A more detailed roadmap and task breakdown can be found in
[`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).
