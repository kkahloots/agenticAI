"""Memory Manager - central memory management for agentic AI."""
from __future__ import annotations
from typing import Any
from datetime import datetime


class MemoryStore:
    """Base memory store."""
    def __init__(self):
        self._store: dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        self._store[key] = {"value": value, "timestamp": datetime.now().isoformat()}
    
    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        return entry["value"] if entry else None
    
    def delete(self, key: str) -> None:
        self._store.pop(key, None)
    
    def clear(self) -> None:
        self._store.clear()


class ConversationMemory(MemoryStore):
    """Short-term conversation memory."""
    def add_message(self, session_id: str, role: str, content: str) -> None:
        key = f"conv:{session_id}"
        messages = self.get(key) or []
        messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        self.set(key, messages)
    
    def get_conversation(self, session_id: str) -> list[dict]:
        return self.get(f"conv:{session_id}") or []


class UserProfileMemory(MemoryStore):
    """Long-term user profile memory."""
    def update_preference(self, user_id: str, key: str, value: Any) -> None:
        profile_key = f"profile:{user_id}"
        profile = self.get(profile_key) or {}
        profile[key] = value
        self.set(profile_key, profile)
    
    def get_profile(self, user_id: str) -> dict:
        return self.get(f"profile:{user_id}") or {}


class InteractionMemory(MemoryStore):
    """Past interactions and outcomes."""
    def record_interaction(self, user_id: str, interaction_type: str, data: dict) -> None:
        key = f"interactions:{user_id}"
        interactions = self.get(key) or []
        interactions.append({
            "type": interaction_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.set(key, interactions)
    
    def get_interactions(self, user_id: str) -> list[dict]:
        return self.get(f"interactions:{user_id}") or []


class AgentObservationMemory(MemoryStore):
    """Agent learnings and observations."""
    def record_observation(self, agent_id: str, observation: str, context: dict) -> None:
        key = f"observations:{agent_id}"
        observations = self.get(key) or []
        observations.append({
            "observation": observation,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self.set(key, observations)
    
    def get_observations(self, agent_id: str) -> list[dict]:
        return self.get(f"observations:{agent_id}") or []


class MemoryManager:
    """Central memory manager coordinating all memory types."""
    
    def __init__(self):
        self.conversation = ConversationMemory()
        self.user_profile = UserProfileMemory()
        self.interaction = InteractionMemory()
        self.agent_observation = AgentObservationMemory()
    
    def clear_all(self) -> None:
        """Clear all memory stores."""
        self.conversation.clear()
        self.user_profile.clear()
        self.interaction.clear()
        self.agent_observation.clear()


# Global memory manager instance
memory_manager = MemoryManager()
