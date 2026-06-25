from collections.abc import Callable
from typing import Any

from nodex.decorators import get_middlewares
from nodex.decorators import middleware as _middleware
from nodex.decorators import node as _node
from nodex.decorators import route as _route
from nodex.display import Display
from nodex.errors import ErrorHandler
from nodex.exceptions import NodexConfigError
from nodex.graph import build_graph
from nodex.middleware import MiddlewareEngine
from nodex.state import NodexState
from nodex.tracer import Tracer
from nodex.types import ExecutionTrace, FlowConfig


class Agent:
    def __init__(self, name: str = "agent", debug: bool = False):
        self.config = FlowConfig(name=name, debug=debug)
        self.tracer = Tracer(name)
        self.display = Display(debug)
        self.error_handler = ErrorHandler(self.tracer, self.display)
        self._entry_node: str | None = None

    def node(
        self,
        next: str = "end",
        retry: int = 0,
        on_fail: str = "raise",
        timeout: float | None = None,
        human_review: bool = False,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            wrapped = _node(
                next=next,
                retry=retry,
                on_fail=on_fail,
                timeout=timeout,
                human_review=human_review,
            )(func)

            if self._entry_node is None:
                self._entry_node = func.__name__

            return wrapped

        return decorator

    def middleware(self, func: Callable) -> Callable:
        return _middleware(func)

    def route(
        self,
        condition: Callable[[NodexState], bool],
        if_true: str,
        if_false: str,
    ) -> Callable:
        return _route(condition=condition, if_true=if_true, if_false=if_false)

    def run(
        self,
        initial_state: dict[str, Any] | None = None,
        raise_errors: bool = True,
    ) -> ExecutionTrace:
        if self._entry_node is None:
            raise NodexConfigError("No nodes registered. Use @app.node() to register nodes.")

        self.tracer.reset()
        state = NodexState()
        state.update(initial_state or {})
        state._current_node = self._entry_node

        self.display.print_header(self.config.name)

        from nodex.decorators import _runtime_context

        middlewares = get_middlewares()
        engine = MiddlewareEngine(middlewares)

        _runtime_context["engine"] = engine
        _runtime_context["tracer"] = self.tracer
        _runtime_context["error_handler"] = self.error_handler
        _runtime_context["display"] = self.display

        compiled_graph = build_graph(self._entry_node)

        try:
            compiled_graph.invoke(state.to_graph_state())
        except Exception:
            trace = self.tracer.get_trace()
            self.display.print_trace(trace)
            if raise_errors:
                raise
            trace.success = False
            return trace

        trace = self.tracer.get_trace()
        self.display.print_trace(trace)

        return trace

    def _build(self) -> Any:
        if self._entry_node is None:
            raise NodexConfigError("No entry node found.")
        return build_graph(self._entry_node)
