import pytest

from nodex.decorators import (
    _middlewares,
    _registry,
    get_registry,
    middleware,
    node,
    route,
)
from nodex.exceptions import NodexStateError
from nodex.state import NodexState


class TestNodeDecorator:
    def setup_method(self):
        _registry.clear()
        _middlewares.clear()

    def test_node_registers_in_registry(self):
        @node(next="end")
        def research(state: NodexState):
            return {"result": "data"}

        assert "research" in get_registry()

    def test_node_stores_config(self):
        @node(next="writer", retry=3)
        def research(state: NodexState):
            return {"result": "data"}

        config = get_registry()["research"]["config"]
        assert config.next == "writer"
        assert config.retry == 3

    def test_node_runs_function(self):
        @node(next="end")
        def research(state: NodexState):
            return {"result": "data"}

        state = NodexState()
        state.update({"query": "test"})
        result = research(state)
        assert result.get("result") == "data"

    def test_node_raises_on_invalid_output(self):
        @node(next="end")
        def bad_node(state: NodexState):
            return "not a dict"

        state = NodexState()
        with pytest.raises(NodexStateError):
            bad_node(state)

    def test_node_default_config(self):
        @node()
        def research(state: NodexState):
            return {"result": "data"}

        config = get_registry()["research"]["config"]
        assert config.next == "end"
        assert config.retry == 0
        assert config.on_fail == "raise"
        assert config.timeout == 30.0

    def test_node_updates_trace(self):
        @node(next="end")
        def research(state: NodexState):
            return {"result": "data"}

        state = NodexState()
        result_state = research(state)
        assert "research" in result_state._trace

    def test_route_registers_when_applied_after_node(self):
        @route(condition=lambda state: True, if_true="publish", if_false="review")
        @node(next="end")
        def research(state: NodexState):
            return {"result": "data"}

        route_config = get_registry()["research"]["route"]
        assert route_config["if_true"] == "publish"
        assert route_config["if_false"] == "review"

    def test_route_registers_when_applied_before_node(self):
        @node(next="end")
        @route(condition=lambda state: True, if_true="publish", if_false="review")
        def research(state: NodexState):
            return {"result": "data"}

        route_config = get_registry()["research"]["route"]
        assert route_config["if_true"] == "publish"
        assert route_config["if_false"] == "review"


class TestMiddlewareDecorator:
    def setup_method(self):
        _registry.clear()
        _middlewares.clear()

    def test_middleware_registers(self):
        @middleware
        def logger(state, next_node):
            return next_node(state)

        assert len(_middlewares) == 1

    def test_middleware_runs_before_node(self):
        called_order = []

        @middleware
        def logger(state, next_node):
            called_order.append("middleware")
            return next_node(state)

        assert "middleware" not in called_order
