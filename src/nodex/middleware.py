from collections.abc import Callable

from nodex.exceptions import NodexMiddlewareError
from nodex.state import NodexState


class MiddlewareEngine:
    def __init__(self, middlewares: list):
        self.middlewares = middlewares

    def execute(self, node_func: Callable, state: NodexState) -> NodexState:
        def build_chain(index: int) -> Callable:
            if index == len(self.middlewares):
                return node_func

            current = self.middlewares[index]
            next_in_chain = build_chain(index + 1)

            def chain(s: NodexState) -> NodexState:
                try:
                    return current(s, next_in_chain)
                except Exception as e:
                    raise NodexMiddlewareError(
                        middleware_name=current.__name__,
                        reason=str(e),
                    ) from e

            return chain

        chain = build_chain(0)
        return chain(state)

    def add(self, middleware: Callable) -> None:
        self.middlewares.append(middleware)

    def has_middlewares(self) -> bool:
        return len(self.middlewares) > 0
