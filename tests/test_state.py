import pytest

from nodex.exceptions import NodexStateError
from nodex.state import NodexState, StateManager


class TestNodexState:
    def test_initial_state_is_empty(self):
        state = NodexState()
        assert state.data == {}
        assert state._current_node == ""
        assert state._trace == []
        assert state._retry_count == 0

    def test_get_existing_key(self, state):
        assert state.get("query") == "test query"

    def test_get_missing_key_returns_default(self, state):
        assert state.get("missing_key") is None
        assert state.get("missing_key", "default") == "default"

    def test_set_key(self, state):
        state.set("new_key", "new_value")
        assert state.get("new_key") == "new_value"

    def test_update_merges_dict(self, state):
        state.update({"key1": "val1", "key2": "val2"})
        assert state.get("key1") == "val1"
        assert state.get("key2") == "val2"

    def test_update_does_not_lose_existing_data(self, state):
        state.update({"new_key": "new_value"})
        assert state.get("query") == "test query"

    def test_trace_starts_empty(self):
        state = NodexState()
        assert state._trace == []

    def test_retry_count_starts_zero(self):
        state = NodexState()
        assert state._retry_count == 0


class TestStateManager:
    def test_infer_fields_stores_node_name(self):
        manager = StateManager()
        manager.infer_fields("research", {"results": [], "confidence": 0.9})
        assert manager.known_fields["results"] == "research"
        assert manager.known_fields["confidence"] == "research"

    def test_infer_fields_does_not_overwrite_existing(self):
        manager = StateManager()
        manager.infer_fields("research", {"results": []})
        manager.infer_fields("writer", {"results": []})
        assert manager.known_fields["results"] == "research"

    def test_validate_passes_valid_dict(self):
        manager = StateManager()
        manager.validate("research", {"results": "data"})

    def test_validate_raises_on_non_dict(self):
        manager = StateManager()
        with pytest.raises(NodexStateError):
            manager.validate("research", "not a dict")

    def test_validate_raises_on_empty_dict(self):
        manager = StateManager()
        with pytest.raises(NodexStateError):
            manager.validate("research", {})

    def test_merge_updates_state(self, state):
        manager = StateManager()
        updated = manager.merge(state, {"research_results": "some results"})
        assert updated.get("research_results") == "some results"

    def test_merge_preserves_existing_state(self, state):
        manager = StateManager()
        updated = manager.merge(state, {"new_key": "new_value"})
        assert updated.get("query") == "test query"
