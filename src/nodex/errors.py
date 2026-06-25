import time

from nodex.display import Display
from nodex.exceptions import NodexNodeError
from nodex.state import NodexState
from nodex.tracer import Tracer


class ErrorHandler:
    def __init__(self, tracer: Tracer, display: Display):
        self.tracer = tracer
        self.display = display

    def handle(
        self,
        error: Exception,
        node_name: str,
        state: NodexState,
        on_fail: str,
        attempt: int,
        max_retries: int,
    ) -> NodexState:
        if self.should_retry(attempt, max_retries):
            return self._handle_retry(node_name, attempt, max_retries, state)

        if on_fail == "raise":
            return self._handle_raise(error, node_name, state)
        elif on_fail == "skip":
            return self._handle_skip(node_name, state)
        else:
            return self._handle_fallback(node_name, on_fail, state)

    def should_retry(self, attempt: int, max_retries: int) -> bool:
        return attempt < max_retries

    def _handle_retry(
        self,
        node_name: str,
        attempt: int,
        max_retries: int,
        state: NodexState,
    ) -> NodexState:
        self.display.print_retrying_live(node_name, attempt + 1, max_retries)
        state._retry_count += 1
        time.sleep(1.0)
        return state

    def _handle_raise(
        self,
        error: Exception,
        node_name: str,
        state: NodexState,
    ) -> NodexState:
        self.tracer.record_error(
            node_name=node_name,
            error=str(error),
            retries=state._retry_count,
        )
        self.display.print_error(
            node_name=node_name,
            reason=str(error),
            trace=state._trace,
        )
        raise NodexNodeError(
            node_name=node_name,
            reason=str(error),
            trace=state._trace,
        )

    def _handle_skip(
        self,
        node_name: str,
        state: NodexState,
    ) -> NodexState:
        self.tracer.record_skip(node_name)
        self.display.print_node_result(self.tracer.results[-1])
        state._trace.append(node_name)
        return state

    def _handle_fallback(
        self,
        node_name: str,
        fallback_node: str,
        state: NodexState,
    ) -> NodexState:
        self.tracer.record_error(
            node_name=node_name,
            error=f"Failed - redirecting to fallback: {fallback_node}",
            retries=state._retry_count,
        )
        self.display.print_error(
            node_name=node_name,
            reason=f"Redirecting to fallback node: {fallback_node}",
            trace=state._trace,
        )
        state._current_node = fallback_node
        state._trace.append(node_name)
        return state
