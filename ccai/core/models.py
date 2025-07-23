# ccai/core/models.py

import time
import uuid
from typing import Any, List, Dict, Literal, Union

from pydantic import BaseModel, Field

class PropertySpec(BaseModel):
    """Defines a property with a value and a calculated confidence score."""
    value: Union[str, float]
    # This score is now calculated from frequency: count(value) / total_count
    score: float = 1.0

class ConceptNode(BaseModel):
    """The fundamental unit of knowledge in the concept graph."""
    name: str
    ctype: Literal[
        "entity", "object", "agent", "state", "event", "quality", "relation", "function"
    ]
    inherits_from: List[str] = Field(default_factory=list)
    
    # This now stores the list of property values with their calculated scores.
    properties: Dict[str, List[PropertySpec]] = Field(default_factory=dict)
    
    # --- NEW FIELD ---
    # This tracks the raw counts for each property value learned.
    # Example: {"color": {"yellow": 4, "green": 1}}
    property_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict)

    structure: Dict[str, List[str]] = Field(default_factory=dict)
    relations: Dict[str, List[str]] = Field(default_factory=dict)
    functions: Dict[str, List[str]] = Field(default_factory=dict)
    logic: Dict[str, Any] = Field(default_factory=dict)
    activation: float = 0.0
    priors: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {"created": time.time(), "usage": 0}
    )

class Signal(BaseModel):
    """The runtime object that travels the graph to reason or assert information."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    origin: str
    purpose: Literal["QUERY", "ASSERT", "OBSERVE", "VERIFY"]
    payload: Dict[str, Any]
    confidence: float = 1.0
    history: List[tuple[str, str, float]] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
