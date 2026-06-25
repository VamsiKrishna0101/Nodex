from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from nodex.state import NodexState


@dataclass
class NodeTestResult:
    success: bool
    output: dict | None
    error: str | None
    duration: float
    state: NodexState


def test_node(
    func: Callable,
    initial_state: dict[str, Any] | None = None,
) -> NodeTestResult:
    import time

    state = NodexState()
    state.update(initial_state or {})
    state._current_node = func.__name__

    start = time.time()

    try:
        output = func(state)
        duration = round(time.time() - start, 3)

        if isinstance(output, NodexState):
            output = output.data

        if not isinstance(output, dict):
            return NodeTestResult(
                success=False,
                output=None,
                error=f"Node must return a dict, got {type(output).__name__}",
                duration=duration,
                state=state,
            )

        state.update(output)

        return NodeTestResult(
            success=True,
            output=output,
            error=None,
            duration=duration,
            state=state,
        )

    except Exception as e:
        duration = round(time.time() - start, 3)
        return NodeTestResult(
            success=False,
            output=None,
            error=str(e),
            duration=duration,
            state=state,
        )


def assert_node_output(
    func: Callable,
    initial_state: dict[str, Any],
    expected_keys: list[str],
) -> NodeTestResult:
    result = test_node(func, initial_state)

    if not result.success:
        raise AssertionError(f"Node '{func.__name__}' failed: {result.error}")

    missing_keys = [key for key in expected_keys if key not in result.output]

    if missing_keys:
        raise AssertionError(
            f"Node '{func.__name__}' output missing keys: {missing_keys}"
        )

    return result


def make_state(data: dict[str, Any] | None = None) -> NodexState:
    state = NodexState()
    state.update(data or {})
    return state
