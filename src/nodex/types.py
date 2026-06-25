from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class NodeResult:
    node_name: str
    status: NodeStatus
    output: Any = None
    duration: float = 0.0
    error: str | None = None
    retries: int = 0
    tokens: int = 0
    cost: float = 0.0


@dataclass
class ExecutionTrace:
    agent_name: str
    results: list[NodeResult] = field(default_factory=list)
    total_duration: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0
    success: bool = True

@dataclass
class RetryConfig:
    max_retries: int = 3
    delay: float = 1.0
    backoff: float = 2.0


@dataclass
class FlowConfig:
    name: str = "agent"
    max_retries: int = 3
    debug: bool = False

@dataclass
class MiddlewareContext:
    node_name: str
    state: Any
    attempt: int = 0
    metadata: dict = field(default_factory=dict)
