"""Tests for memory manager."""

import pytest
from memory.memory_manager import (
    MemoryStore,
    ConversationMemory,
    UserProfileMemory,
    InteractionMemory,
    AgentObservationMemory,
    MemoryManager,
    memory_manager,
)


class TestMemoryStore:
    """Test base MemoryStore class."""

    def test_set_and_get(self):
        """Test setting and getting values."""
        store = MemoryStore()
        store.set("key1", "value1")
        assert store.get("key1") == "value1"

    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        store = MemoryStore()
        assert store.get("nonexistent") is None

    def test_delete(self):
        """Test deleting a key."""
        store = MemoryStore()
        store.set("key1", "value1")
        store.delete("key1")
        assert store.get("key1") is None

    def test_delete_nonexistent_key(self):
        """Test deleting non-existent key doesn't raise error."""
        store = MemoryStore()
        store.delete("nonexistent")  # Should not raise

    def test_clear(self):
        """Test clearing all memory."""
        store = MemoryStore()
        store.set("key1", "value1")
        store.set("key2", "value2")
        store.clear()
        assert store.get("key1") is None
        assert store.get("key2") is None

    def test_set_overwrites_existing(self):
        """Test that set overwrites existing values."""
        store = MemoryStore()
        store.set("key1", "value1")
        store.set("key1", "value2")
        assert store.get("key1") == "value2"

    def test_set_stores_timestamp(self):
        """Test that set stores timestamp."""
        store = MemoryStore()
        store.set("key1", "value1")
        entry = store._store["key1"]
        assert "timestamp" in entry
        assert "value" in entry


class TestConversationMemory:
    """Test ConversationMemory class."""

    def test_add_message(self):
        """Test adding a message."""
        conv = ConversationMemory()
        conv.add_message("session1", "user", "Hello")
        messages = conv.get_conversation("session1")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        conv = ConversationMemory()
        conv.add_message("session1", "user", "Hello")
        conv.add_message("session1", "assistant", "Hi there")
        messages = conv.get_conversation("session1")
        assert len(messages) == 2

    def test_get_conversation_empty(self):
        """Test getting empty conversation."""
        conv = ConversationMemory()
        messages = conv.get_conversation("nonexistent")
        assert messages == []

    def test_separate_sessions(self):
        """Test that different sessions are separate."""
        conv = ConversationMemory()
        conv.add_message("session1", "user", "Message 1")
        conv.add_message("session2", "user", "Message 2")
        
        messages1 = conv.get_conversation("session1")
        messages2 = conv.get_conversation("session2")
        
        assert len(messages1) == 1
        assert len(messages2) == 1
        assert messages1[0]["content"] == "Message 1"
        assert messages2[0]["content"] == "Message 2"


class TestUserProfileMemory:
    """Test UserProfileMemory class."""

    def test_update_preference(self):
        """Test updating user preference."""
        profile = UserProfileMemory()
        profile.update_preference("user1", "language", "en")
        user_profile = profile.get_profile("user1")
        assert user_profile["language"] == "en"

    def test_update_multiple_preferences(self):
        """Test updating multiple preferences."""
        profile = UserProfileMemory()
        profile.update_preference("user1", "language", "en")
        profile.update_preference("user1", "timezone", "UTC")
        user_profile = profile.get_profile("user1")
        assert user_profile["language"] == "en"
        assert user_profile["timezone"] == "UTC"

    def test_get_profile_empty(self):
        """Test getting empty profile."""
        profile = UserProfileMemory()
        user_profile = profile.get_profile("nonexistent")
        assert user_profile == {}

    def test_update_overwrites_preference(self):
        """Test that updating overwrites existing preference."""
        profile = UserProfileMemory()
        profile.update_preference("user1", "language", "en")
        profile.update_preference("user1", "language", "fr")
        user_profile = profile.get_profile("user1")
        assert user_profile["language"] == "fr"


class TestInteractionMemory:
    """Test InteractionMemory class."""

    def test_record_interaction(self):
        """Test recording an interaction."""
        interaction = InteractionMemory()
        interaction.record_interaction("user1", "knowledge_retrieval", {"query": "test"})
        interactions = interaction.get_interactions("user1")
        assert len(interactions) == 1
        assert interactions[0]["type"] == "knowledge_retrieval"
        assert interactions[0]["data"]["query"] == "test"

    def test_record_multiple_interactions(self):
        """Test recording multiple interactions."""
        interaction = InteractionMemory()
        interaction.record_interaction("user1", "knowledge_retrieval", {"query": "test1"})
        interaction.record_interaction("user1", "analytics", {"query": "test2"})
        interactions = interaction.get_interactions("user1")
        assert len(interactions) == 2

    def test_get_interactions_empty(self):
        """Test getting empty interactions."""
        interaction = InteractionMemory()
        interactions = interaction.get_interactions("nonexistent")
        assert interactions == []

    def test_separate_users(self):
        """Test that different users have separate interactions."""
        interaction = InteractionMemory()
        interaction.record_interaction("user1", "type1", {"data": "1"})
        interaction.record_interaction("user2", "type2", {"data": "2"})
        
        interactions1 = interaction.get_interactions("user1")
        interactions2 = interaction.get_interactions("user2")
        
        assert len(interactions1) == 1
        assert len(interactions2) == 1


class TestAgentObservationMemory:
    """Test AgentObservationMemory class."""

    def test_record_observation(self):
        """Test recording an observation."""
        obs = AgentObservationMemory()
        obs.record_observation("agent1", "Found pattern X", {"context": "data"})
        observations = obs.get_observations("agent1")
        assert len(observations) == 1
        assert observations[0]["observation"] == "Found pattern X"

    def test_record_multiple_observations(self):
        """Test recording multiple observations."""
        obs = AgentObservationMemory()
        obs.record_observation("agent1", "Observation 1", {})
        obs.record_observation("agent1", "Observation 2", {})
        observations = obs.get_observations("agent1")
        assert len(observations) == 2

    def test_get_observations_empty(self):
        """Test getting empty observations."""
        obs = AgentObservationMemory()
        observations = obs.get_observations("nonexistent")
        assert observations == []

    def test_separate_agents(self):
        """Test that different agents have separate observations."""
        obs = AgentObservationMemory()
        obs.record_observation("agent1", "Obs 1", {})
        obs.record_observation("agent2", "Obs 2", {})
        
        obs1 = obs.get_observations("agent1")
        obs2 = obs.get_observations("agent2")
        
        assert len(obs1) == 1
        assert len(obs2) == 1


class TestMemoryManager:
    """Test MemoryManager class."""

    def test_memory_manager_has_all_stores(self):
        """Test that MemoryManager has all memory stores."""
        mm = MemoryManager()
        assert isinstance(mm.conversation, ConversationMemory)
        assert isinstance(mm.user_profile, UserProfileMemory)
        assert isinstance(mm.interaction, InteractionMemory)
        assert isinstance(mm.agent_observation, AgentObservationMemory)

    def test_clear_all(self):
        """Test clearing all memory stores."""
        mm = MemoryManager()
        mm.conversation.add_message("session1", "user", "Hello")
        mm.user_profile.update_preference("user1", "lang", "en")
        mm.interaction.record_interaction("user1", "type", {})
        mm.agent_observation.record_observation("agent1", "obs", {})
        
        mm.clear_all()
        
        assert mm.conversation.get_conversation("session1") == []
        assert mm.user_profile.get_profile("user1") == {}
        assert mm.interaction.get_interactions("user1") == []
        assert mm.agent_observation.get_observations("agent1") == []

    def test_global_memory_manager_instance(self):
        """Test that global memory_manager instance exists."""
        assert memory_manager is not None
        assert isinstance(memory_manager, MemoryManager)

    def test_memory_manager_independent_stores(self):
        """Test that memory stores are independent."""
        mm = MemoryManager()
        mm.conversation.add_message("session1", "user", "Hello")
        mm.user_profile.update_preference("user1", "lang", "en")
        
        # Clear only conversation
        mm.conversation.clear()
        
        assert mm.conversation.get_conversation("session1") == []
        assert mm.user_profile.get_profile("user1") == {"lang": "en"}
