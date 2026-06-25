from typing import Any

from nodex.exceptions import NodexStateError


class NodexState:
    _INTERNAL_KEYS = {"_current_node", "_trace", "_retry_count"}

    def __init__(self, data: dict | None = None):
        # Accept NodexState as input (for test compatibility)
        if isinstance(data, NodexState):
            self.data = data.data
            self._internal = data._internal
            return

        self.data = dict(data or {})
        # Separate internal state from user data
        self._internal = {
            "_current_node": self.data.pop("_current_node", ""),
            "_trace": self.data.pop("_trace", []),
            "_retry_count": self.data.pop("_retry_count", 0),
        }

    @property
    def _current_node(self) -> str:
        return self._internal["_current_node"]

    @_current_node.setter
    def _current_node(self, value: str):
        self._internal["_current_node"] = value

    @property
    def _trace(self) -> list:
        return self._internal["_trace"]

    @_trace.setter
    def _trace(self, value: list):
        self._internal["_trace"] = value

    @property
    def _retry_count(self) -> int:
        return self._internal["_retry_count"]

    @_retry_count.setter
    def _retry_count(self, value: int):
        self._internal["_retry_count"] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def update(self, new_data: dict) -> None:
        # Don't let user updates overwrite internal keys
        for k, v in new_data.items():
            if k not in self._INTERNAL_KEYS:
                self.data[k] = v

    def to_graph_state(self) -> dict:
        """Return state shaped for LangGraph, including Nodex internals."""
        graph_state = dict(self.data)
        graph_state["_current_node"] = self._current_node
        graph_state["_trace"] = list(self._trace)
        graph_state["_retry_count"] = self._retry_count
        return graph_state


class StateManager:
    def __init__(self):
        self.known_fields = {}

    def infer_fields(self, node_name: str, output: dict) -> None:
        for key in output:
            if key not in self.known_fields:
                self.known_fields[key] = node_name

    def validate(self, node_name: str, output: Any) -> None:
        if not isinstance(output, dict):
            raise NodexStateError(node_name, f"Output must be a dict, got {type(output).__name__}")
        if not output:
            raise NodexStateError(node_name, "Node returned empty output")

    def merge(self, state: NodexState, output: dict) -> NodexState:
        state.update(output)
        return state
