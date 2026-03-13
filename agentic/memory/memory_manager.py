"""Memory Manager for tracking agent execution history."""

from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntry:
    """Single memory entry."""
    timestamp: str
    entry_type: str  # plan, tool_usage, compliance_decision, sql_generation, observation
    data: dict
    request_id: Optional[str] = None


class MemoryManager:
    """Manages execution memory across agent runs."""
    
    def __init__(self):
        self._entries: list[MemoryEntry] = []
        self._by_request: dict[str, list[MemoryEntry]] = {}
    
    def record_plan(self, request_id: str, plan: dict):
        """Record a generated plan."""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            entry_type="plan",
            data=plan,
            request_id=request_id
        )
        self._add_entry(entry)
    
    def record_tool_usage(self, request_id: str, tool_name: str, args: dict, result: Any):
        """Record tool execution."""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            entry_type="tool_usage",
            data={"tool_name": tool_name, "args": args, "result": result},
            request_id=request_id
        )
        self._add_entry(entry)
    
    def record_sql_generation(self, request_id: str, query: str, intent: str):
        """Record SQL generation."""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            entry_type="sql_generation",
            data={"query": query, "intent": intent},
            request_id=request_id
        )
        self._add_entry(entry)
    
    def record_compliance_decision(self, request_id: str, decision: dict):
        """Record compliance check decision."""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            entry_type="compliance_decision",
            data=decision,
            request_id=request_id
        )
        self._add_entry(entry)
    
    def record_observation(self, request_id: str, observation: str):
        """Record agent observation."""
        entry = MemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            entry_type="observation",
            data={"observation": observation},
            request_id=request_id
        )
        self._add_entry(entry)
    
    def _add_entry(self, entry: MemoryEntry):
        """Add entry to memory."""
        self._entries.append(entry)
        if entry.request_id:
            if entry.request_id not in self._by_request:
                self._by_request[entry.request_id] = []
            self._by_request[entry.request_id].append(entry)
    
    def get_request_history(self, request_id: str) -> list[MemoryEntry]:
        """Get all entries for a request."""
        return self._by_request.get(request_id, [])
    
    def get_recent_entries(self, n: int = 10) -> list[MemoryEntry]:
        """Get n most recent entries."""
        return self._entries[-n:]
    
    def clear(self):
        """Clear all memory."""
        self._entries.clear()
        self._by_request.clear()


# Global memory instance
_memory = MemoryManager()


def get_memory() -> MemoryManager:
    """Get the global memory manager."""
    return _memory
