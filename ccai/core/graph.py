# ccai/core/graph.py

from pathlib import Path
from typing import Dict, Optional, List
import time

from ccai.core.models import ConceptNode, PropertySpec
from ccai.io.persistence import GraphPersistence

class ConceptGraph:
    """The main in-memory representation and manager of the knowledge graph."""

    def __init__(self, storage_path: Path):
        self._nodes: Dict[str, ConceptNode] = {}
        self._persistence = GraphPersistence(storage_path)

    def load_from_disk(self):
        """Loads the graph state from the disk by loading the last snapshot
        and replaying any subsequent mutations from the WAL."""
        self._nodes, last_snapshot_ts = self._persistence.load_snapshot()
        mutations = self._persistence.load_mutations_after(last_snapshot_ts)
        if mutations:
            print("Replaying new mutations...")
            self._replay_mutations(mutations)
    
    def get_node(self, name: str) -> Optional[ConceptNode]:
        """Retrieves a node by name or any of its aliases."""
        clean = name.lower().strip()
        node = self._nodes.get(clean)
        if node:
            return node

        for n in self._nodes.values():
            if clean in [a.lower() for a in n.aliases]:
                return n

        return None

    def add_node(self, node: ConceptNode):
        """Adds a new node to the graph and logs the mutation."""
        if node.name in self._nodes:
            # For simplicity, we'll just log an update. A real system might merge.
            print(f"Node '{node.name}' already exists. Updating.")
        self._nodes[node.name] = node
        self._persistence.log_mutation("ADD_NODE", node_data=node.model_dump())

    def update_property(self, node_name: str, category: str, value: str):
        """Increment property statistics and recalc scores safely."""
        node = self.get_node(node_name)
        if not node:
            return
        stats = node.property_stats.setdefault(category, {})
        stats[value] = stats.get(value, 0) + 1
        total = sum(stats.values())
        node.properties[category] = [
            PropertySpec(value=v, score=(c / total if total else 1.0))
            for v, c in stats.items()
        ]
        node.metadata["last_updated"] = time.time()
        self._persistence.log_mutation(
            "UPDATE_PROPERTY",
            node=node_name,
            category=category,
            value=value,
        )

    def add_edge(self, src_name: str, relation_type: str, dst_name: str):
        """Adds a new directional edge between two nodes and logs the mutation."""
        source_node = self.get_node(src_name)
        dest_node = self.get_node(dst_name)

        if not source_node or not dest_node:
            print(f"Error: Cannot create edge. Source '{src_name}' or destination '{dst_name}' not found.")
            return
            
        # This is a simplified example. Your full spec has different edge dicts.
        # We'll add to the generic 'relations' dict for now.
        if relation_type not in source_node.relations:
            source_node.relations[relation_type] = []

        if dst_name not in source_node.relations[relation_type]:
            source_node.relations[relation_type].append(dst_name)
            source_node.metadata["last_updated"] = time.time()
            self._persistence.log_mutation(
                "ADD_EDGE", src=src_name, rel=relation_type, dst=dst_name
            )

    def save_snapshot(self):
        """Saves the current state of the graph to a snapshot file."""
        self._persistence.save_snapshot(self._nodes)

    def close(self):
        """Flushes pending WAL entries."""
        self._persistence.stop()

    def _replay_mutations(self, mutations: List[dict]):
        """Applies a list of mutation operations to the current graph state."""
        for mut in mutations:
            op = mut.get("op")
            if op == "ADD_NODE":
                node_data = mut.get("node_data", {})
                if node_data:
                    self._nodes[node_data["name"]] = ConceptNode(**node_data)
            elif op == "ADD_EDGE":
                src, rel, dst = mut.get("src"), mut.get("rel"), mut.get("dst")
                if src and rel and dst and src in self._nodes:
                    if rel not in self._nodes[src].relations:
                        self._nodes[src].relations[rel] = []
                    if dst not in self._nodes[src].relations[rel]:
                        self._nodes[src].relations[rel].append(dst)
            elif op == "UPDATE_PROPERTY":
                node = mut.get("node")
                cat = mut.get("category")
                val = mut.get("value")
                if node and cat and val:
                    self.update_property(node, cat, val)


