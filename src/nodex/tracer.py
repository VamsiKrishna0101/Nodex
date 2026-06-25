import time
from typing import Any

from nodex.types import ExecutionTrace, NodeResult, NodeStatus


class Tracer:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.results: list[NodeResult] = []
        self._start_times: dict[str, float] = {}
        self._run_start: float = time.time()

    def start_node(self, node_name: str) -> None:
        self._start_times[node_name] = time.time()

    def end_node(
        self,
        node_name: str,
        output: Any = None,
        tokens: int = 0,
        retries: int = 0,
    ) -> NodeResult:
        duration = time.time() - self._start_times.get(node_name, time.time())
        cost = self.calculate_cost(tokens)

        result = NodeResult(
            node_name=node_name,
            status=NodeStatus.SUCCESS,
            output=output,
            duration=round(duration, 3),
            tokens=tokens,
            cost=cost,
            retries=retries,
        )

        self.results.append(result)
        return result

    def record_error(
        self,
        node_name: str,
        error: str,
        retries: int = 0,
    ) -> NodeResult:
        duration = time.time() - self._start_times.get(node_name, time.time())

        result = NodeResult(
            node_name=node_name,
            status=NodeStatus.FAILURE,
            output=None,
            duration=round(duration, 3),
            error=error,
            retries=retries,
        )

        self.results.append(result)
        return result

    def record_skip(self, node_name: str) -> NodeResult:
        result = NodeResult(
            node_name=node_name,
            status=NodeStatus.SKIPPED,
            output=None,
            duration=0.0,
        )

        self.results.append(result)
        return result

    def get_trace(self) -> ExecutionTrace:
        total_duration = round(time.time() - self._run_start, 3)
        total_tokens = sum(r.tokens for r in self.results)
        total_cost = round(sum(r.cost for r in self.results), 6)
        success = all(r.status == NodeStatus.SUCCESS or r.status == NodeStatus.SKIPPED for r in self.results)

        return ExecutionTrace(
            agent_name=self.agent_name,
            results=self.results,
            total_duration=total_duration,
            total_tokens=total_tokens,
            total_cost=total_cost,
            success=success,
        )

    def calculate_cost(self, tokens: int) -> float:
        cost_per_1k_tokens = 0.002
        return round((tokens / 1000) * cost_per_1k_tokens, 6)

    def reset(self) -> None:
        self.results = []
        self._start_times = {}
        self._run_start = time.time()
