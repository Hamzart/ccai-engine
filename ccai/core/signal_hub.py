"""Priority based queue for managing signals during reasoning."""

from __future__ import annotations

import heapq
from typing import List, Tuple, Optional

from ccai.core.models import Signal


class SignalHub:
    """A simple priority queue ordered by signal confidence."""

    def __init__(self) -> None:
        self._queue: List[Tuple[float, int, Signal]] = []
        self._counter = 0

    def push(self, signal: Signal) -> None:
        self._counter += 1
        heapq.heappush(self._queue, (-signal.confidence, self._counter, signal))

    def pop(self) -> Optional[Signal]:
        if not self._queue:
            return None
        _, _, sig = heapq.heappop(self._queue)
        return sig

    def empty(self) -> bool:
        return len(self._queue) == 0
