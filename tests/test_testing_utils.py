from nodex.decorators import node
from nodex.testing import assert_node_output, make_state
from nodex.testing import test_node as run_test_node


class TestTestingUtils:
    def test_test_node_accepts_plain_node(self):
        def start(state):
            return {"answer": state.get("query")}

        result = run_test_node(start, {"query": "hello"})

        assert result.success is True
        assert result.output == {"answer": "hello"}

    def test_test_node_accepts_decorated_node(self):
        @node(next="end")
        def start(state):
            return {"answer": "decorated"}

        result = run_test_node(start)

        assert result.success is True
        assert result.output == {"answer": "decorated"}

    def test_assert_node_output_returns_result(self):
        def start(state):
            return {"answer": "ok"}

        result = assert_node_output(start, {}, ["answer"])

        assert result.success is True

    def test_make_state_uses_provided_data(self):
        state = make_state({"query": "hello"})

        assert state.get("query") == "hello"
