from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from functools import wraps
from typing import Any

from nodex.exceptions import NodexNodeError, NodexTimeoutError
from nodex.state import NodexState, StateManager


@dataclass
class NodeConfig:
    next: str = "end"
    retry: int = 0
    on_fail: str = "raise"
    timeout: float = 30.0
    human_review: bool = False
    middlewares: list = field(default_factory=list)


_registry: dict[str, dict] = {}
_middlewares: list[Callable] = []

_runtime_context: dict[str, Any] = {}


def node(
    next: str = "end",
    retry: int = 0,
    on_fail: str = "raise",
    timeout: float = 30.0,
    human_review: bool = False,
):
    config = NodeConfig(
        next=next,
        retry=retry,
        on_fail=on_fail,
        timeout=timeout,
        human_review=human_review,
    )

    def decorator(func: Callable) -> Callable:
        state_manager = StateManager()
        func._nodex_config = config

        @wraps(func)
        def wrapper(state_dict) -> dict:
            tracer = _runtime_context.get("tracer")
            error_handler = _runtime_context.get("error_handler")
            engine = _runtime_context.get("engine")
            display = _runtime_context.get("display")

            # Accept both dict (from LangGraph) and NodexState (from tests)
            _called_with_state = isinstance(state_dict, NodexState)
            if _called_with_state:
                nodex_state = state_dict
            else:
                nodex_state = NodexState(state_dict)

            if tracer:
                tracer.start_node(func.__name__)

            attempts = 0

            while attempts <= config.retry:
                try:
                    if engine and engine.has_middlewares():
                        def run_node(current_state=nodex_state):
                            return engine.execute(func, current_state)
                    else:
                        def run_node(current_state=nodex_state):
                            return func(current_state)

                    # --- Timeout enforcement ---
                    if config.timeout and config.timeout > 0:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(run_node)
                            try:
                                output = future.result(timeout=config.timeout)
                            except FuturesTimeoutError as e:
                                raise NodexTimeoutError(func.__name__, config.timeout) from e
                    else:
                        output = run_node()

                    node_tokens = output.pop("_tokens", 0) if isinstance(output, dict) else 0

                    state_manager.validate(func.__name__, output)
                    state_manager.infer_fields(func.__name__, output)
                    nodex_state = state_manager.merge(nodex_state, output)
                    nodex_state._current_node = config.next
                    nodex_state._trace.append(func.__name__)

                    # --- Human-in-the-loop ---
                    if config.human_review:
                        print(f"\n[nodex] Human review required for node '{func.__name__}'")
                        print(f"  Output: {output}")
                        answer = input("  Approve and continue? [y/n]: ").strip().lower()
                        if answer != "y":
                            raise NodexNodeError(
                                node_name=func.__name__,
                                reason="Human reviewer rejected this node's output.",
                                trace=nodex_state._trace,
                            )

                    if tracer:
                        result = tracer.end_node(func.__name__, output=output, tokens=node_tokens, retries=attempts)
                        if display:
                            display.print_node_result(result)

                    return nodex_state if _called_with_state else nodex_state.data

                except Exception as e:
                    if error_handler:
                        nodex_state = error_handler.handle(
                            error=e,
                            node_name=func.__name__,
                            state=nodex_state,
                            on_fail=config.on_fail,
                            attempt=attempts,
                            max_retries=config.retry,
                        )
                        if attempts < nodex_state._retry_count:
                            attempts = nodex_state._retry_count
                            continue
                        else:
                            return nodex_state if _called_with_state else nodex_state.data
                    else:
                        raise e

            return nodex_state if _called_with_state else nodex_state.data

        registered = {
            "func": wrapper,
            "config": config,
        }

        route_config = getattr(func, "_nodex_route", None)
        if route_config:
            registered["route"] = route_config

        _registry[func.__name__] = registered

        return wrapper

    return decorator


def middleware(func: Callable) -> Callable:
    _middlewares.append(func)

    @wraps(func)
    def wrapper(state: NodexState, next_node: Callable) -> NodexState:
        return func(state, next_node)

    return wrapper


def route(
    condition: Callable[[NodexState], bool],
    if_true: str,
    if_false: str,
):
    route_config = {
        "condition": condition,
        "if_true": if_true,
        "if_false": if_false,
    }

    def decorator(func: Callable) -> Callable:
        func._nodex_route = route_config

        @wraps(func)
        def wrapper(state: NodexState) -> NodexState:
            result = func(state)
            if condition(state):
                state._current_node = if_true
            else:
                state._current_node = if_false
            return result

        wrapper._nodex_route = route_config

        if func.__name__ in _registry:
            _registry[func.__name__]["route"] = route_config

        return wrapper

    return decorator


def get_registry() -> dict:
    return _registry


def get_middlewares() -> list:
    return _middlewares


def reset_registry() -> None:
    _registry.clear()
    _middlewares.clear()
    _runtime_context.clear()
