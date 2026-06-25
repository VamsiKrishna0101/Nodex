class NodexError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"[nodex] {self.message}"


class NodexNodeError(NodexError):
    def __init__(self, node_name: str, reason: str, trace: list[str] | None = None):
        self.node_name = node_name
        self.reason = reason
        self.trace = trace or []
        trace_text = " -> ".join(self.trace) if self.trace else "unknown"
        message = (
            f"Node '{node_name}' failed\n"
            f"  - Reason: {reason}\n"
            f"  - Trace: {trace_text} <- HERE"
        )
        super().__init__(message)


class NodexStateError(NodexError):
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        message = f"State validation failed on field '{field}': {reason}"
        super().__init__(message)


class NodexMiddlewareError(NodexError):
    def __init__(self, middleware_name: str, reason: str):
        self.middleware_name = middleware_name
        self.reason = reason
        message = f"Middleware '{middleware_name}' failed: {reason}"
        super().__init__(message)


class NodexRouteError(NodexError):
    def __init__(self, node_name: str, reason: str):
        self.node_name = node_name
        self.reason = reason
        message = f"Routing failed at node '{node_name}': {reason}"
        super().__init__(message)


class NodexConfigError(NodexError):
    def __init__(self, reason: str):
        self.reason = reason
        message = f"Configuration error: {reason}"
        super().__init__(message)


class NodexAuthError(NodexError):
    def __init__(self, reason: str):
        self.reason = reason
        message = f"Auth error: {reason}"
        super().__init__(message)


class NodexTimeoutError(NodexError):
    def __init__(self, node_name: str, timeout: float):
        self.node_name = node_name
        self.timeout = timeout
        message = f"Node '{node_name}' timed out after {timeout}s"
        super().__init__(message)
