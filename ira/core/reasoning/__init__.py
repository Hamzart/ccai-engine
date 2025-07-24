"""
Reasoning module for the IRA architecture.

This module provides the core reasoning functionality for the IRA architecture,
including ideom-based cognition, signal propagation, prefab activation, and learning.
"""

from .ideom import Ideom
from .ideom_network import IdeomNetwork
from .activation_pattern import ActivationPattern
from .signal_propagator import SignalPropagator
from .prefab import Prefab
from .prefab_manager import PrefabManager
from .learning_engine import LearningEngine, Feedback
from .unified_reasoning_core import UnifiedReasoningCore, ReasoningResult

__all__ = [
    'Ideom',
    'IdeomNetwork',
    'ActivationPattern',
    'SignalPropagator',
    'Prefab',
    'PrefabManager',
    'LearningEngine',
    'Feedback',
    'UnifiedReasoningCore',
    'ReasoningResult',
]