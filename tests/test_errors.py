import pytest

from nodex.display import Display
from nodex.errors import ErrorHandler
from nodex.exceptions import NodexNodeError
from nodex.state import NodexState
from nodex.tracer import Tracer


class TestErrorHandler:
    def setup_method(self):
        self.tracer = Tracer("test-agent")
        self.display = Display(debug=False)
        self.handler = ErrorHandler(self.tracer, self.display)

    def test_should_retry_when_attempts_less_than_max(self):
        assert self.handler.should_retry(0, 3)
        assert self.handler.should_retry(1, 3)
        assert self.handler.should_retry(2, 3)

    def test_should_not_retry_when_attempts_equal_max(self):
        assert not self.handler.should_retry(3, 3)

    def test_handle_raise_raises_nodex_node_error(self):
        state = NodexState()
        state._trace = ["start", "research"]
        error = ValueError("something broke")

        with pytest.raises(NodexNodeError):
            self.handler.handle(
                error=error,
                node_name="research",
                state=state,
                on_fail="raise",
                attempt=3,
                max_retries=3,
            )

    def test_handle_skip_returns_state(self):
        state = NodexState()
        self.tracer.start_node("research")
        error = ValueError("something broke")

        result = self.handler.handle(
            error=error,
            node_name="research",
            state=state,
            on_fail="skip",
            attempt=3,
            max_retries=3,
        )

        assert result is not None
        assert "research" in result._trace

    def test_handle_fallback_sets_current_node(self):
        state = NodexState()
        self.tracer.start_node("research")
        error = ValueError("something broke")

        result = self.handler.handle(
            error=error,
            node_name="research",
            state=state,
            on_fail="fallback_research",
            attempt=3,
            max_retries=3,
        )

        assert result._current_node == "fallback_research"
