# ccai/io/persistence.py

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from threading import Thread, Event
from queue import Queue, Empty

import msgpack
from ccai.core.models import ConceptNode

class GraphPersistence:
    """Handles saving and loading the concept graph to disk."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.snapshot_file = storage_path / "snapshot.msgpack"
        self.wal_file = storage_path / "wal.ndjson"

        # Ensure the storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Queue and background thread for async WAL writing
        self._queue: Queue = Queue()
        self._stop_event = Event()
        self._worker = Thread(target=self._process_queue, daemon=True)
        self._worker.start()

    def save_snapshot(self, nodes: Dict[str, ConceptNode]):
        """Saves the entire graph to a compressed msgpack file atomically."""
        payload = {
            "timestamp": time.time(),
            "nodes": {name: node.model_dump() for name, node in nodes.items()}
        }
        
        packed_payload = msgpack.packb(payload)
        
        # Atomic write: write to a temporary file then rename
        tmp_file = self.snapshot_file.with_suffix(".tmp")
        with open(tmp_file, "wb") as f:
            f.write(packed_payload)
        
        os.rename(tmp_file, self.snapshot_file)
        print(f"Graph snapshot saved to {self.snapshot_file}")

    def load_snapshot(self) -> Tuple[Dict[str, ConceptNode], float]:
        """Loads the graph from a snapshot file, if it exists."""
        if not self.snapshot_file.exists():
            return {}, 0.0

        with open(self.snapshot_file, "rb") as f:
            unpacked_payload = msgpack.unpackb(f.read())
        
        nodes_data = unpacked_payload.get("nodes", {})
        nodes = {name: ConceptNode(**data) for name, data in nodes_data.items()}
        timestamp = unpacked_payload.get("timestamp", 0.0)
        
        print(f"Loaded {len(nodes)} nodes from snapshot.")
        return nodes, timestamp

    def log_mutation(self, op: str, **data: Any):
        """Appends a single mutation operation to the Write-Ahead Log."""
        log_entry = {
            "ts": time.time(),
            "op": op,
            **data
        }
        self._queue.put(log_entry)

    def _process_queue(self):
        """Background worker that writes queued mutations to disk."""
        while not self._stop_event.is_set():
            try:
                entry = self._queue.get(timeout=0.1)
            except Empty:
                continue
            with open(self.wal_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
            self._queue.task_done()

    def stop(self):
        """Stops the background writer and flushes remaining entries."""
        self._stop_event.set()
        self._worker.join()
        while True:
            try:
                entry = self._queue.get_nowait()
            except Empty:
                break
            with open(self.wal_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def load_mutations_after(self, timestamp: float) -> List[Dict[str, Any]]:
        """Loads all mutations from the WAL that occurred after the given timestamp."""
        mutations = []
        if not self.wal_file.exists():
            return mutations

        with open(self.wal_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("ts", 0) > timestamp:
                        mutations.append(entry)
                except json.JSONDecodeError:
                    # Ignore corrupted lines
                    continue
        
        print(f"Loaded {len(mutations)} new mutations from WAL.")
        return mutations
