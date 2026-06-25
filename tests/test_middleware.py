import pytest

from nodex.exceptions import NodexMiddlewareError
from nodex.middleware import MiddlewareEngine
from nodex.state import NodexState


class TestMiddlewareEngine:
    def test_no_middleware_runs_node_directly(self):
        engine = MiddlewareEngine([])
        state = NodexState()
        state.update({"query": "test"})

        def node(s):
            s.set("result", "done")
            return s

        result = engine.execute(node, state)
        assert result.get("result") == "done"

    def test_middleware_runs_before_node(self):
        call_order = []

        def logger(state, next_node):
            call_order.append("middleware")
            return next_node(state)

        def node(state):
            call_order.append("node")
            return state

        engine = MiddlewareEngine([logger])
        state = NodexState()
        engine.execute(node, state)

        assert call_order == ["middleware", "node"]

    def test_multiple_middlewares_run_in_order(self):
        call_order = []

        def first(state, next_node):
            call_order.append("first")
            return next_node(state)

        def second(state, next_node):
            call_order.append("second")
            return next_node(state)

        def node(state):
            call_order.append("node")
            return state

        engine = MiddlewareEngine([first, second])
        state = NodexState()
        engine.execute(node, state)

        assert call_order == ["first", "second", "node"]

    def test_middleware_error_raises_nodex_middleware_error(self):
        def broken_middleware(state, next_node):
            raise ValueError("middleware broke")

        def node(state):
            return state

        engine = MiddlewareEngine([broken_middleware])
        state = NodexState()

        with pytest.raises(NodexMiddlewareError):
            engine.execute(node, state)

    def test_node_error_is_not_wrapped_as_middleware_error(self):
        def logger(state, next_node):
            return next_node(state)

        def broken_node(state):
            raise ValueError("provider model not found")

        engine = MiddlewareEngine([logger])
        state = NodexState()

        with pytest.raises(ValueError, match="provider model not found"):
            engine.execute(broken_node, state)

    def test_middleware_error_after_next_is_wrapped(self):
        def broken_after_next(state, next_node):
            next_node(state)
            raise ValueError("middleware post-processing broke")

        def node(state):
            return state

        engine = MiddlewareEngine([broken_after_next])
        state = NodexState()

        with pytest.raises(NodexMiddlewareError, match="middleware post-processing broke"):
            engine.execute(node, state)

    def test_caught_node_error_then_middleware_error_is_wrapped(self):
        def catches_downstream_then_fails(state, next_node):
            try:
                next_node(state)
            except Exception:
                pass
            raise RuntimeError("middleware cleanup failed")

        def broken_node(state):
            raise ValueError("provider model not found")

        engine = MiddlewareEngine([catches_downstream_then_fails])
        state = NodexState()

        with pytest.raises(NodexMiddlewareError, match="middleware cleanup failed"):
            engine.execute(broken_node, state)

    def test_add_middleware(self):
        engine = MiddlewareEngine([])
        assert not engine.has_middlewares()

        def logger(state, next_node):
            return next_node(state)

        engine.add(logger)
        assert engine.has_middlewares()
