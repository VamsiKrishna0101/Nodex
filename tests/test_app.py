import pytest

from nodex import Agent
from nodex.exceptions import NodexConfigError, NodexNodeError


class TestAgent:
    def test_run_executes_registered_nodes(self):
        app = Agent(name="test-agent")

        @app.node(next="writer")
        def start(state):
            return {"message": "hello"}

        @app.node(next="end")
        def writer(state):
            return {"final": f"{state.get('message')} world"}

        trace = app.run()

        assert trace.success is True
        assert [result.node_name for result in trace.results] == ["start", "writer"]
        assert trace.results[-1].output == {"final": "hello world"}

    def test_run_accepts_initial_state(self):
        app = Agent(name="stateful-agent")

        @app.node(next="end")
        def start(state):
            return {"final": state.get("query")}

        trace = app.run({"query": "from initial state"})

        assert trace.results[-1].output == {"final": "from initial state"}

    def test_run_resets_trace_between_runs(self):
        app = Agent(name="repeat-agent")

        @app.node(next="end")
        def start(state):
            return {"value": state.get("value", 1)}

        first = app.run({"value": 1})
        second = app.run({"value": 2})

        assert len(first.results) == 1
        assert len(second.results) == 1
        assert second.results[0].output == {"value": 2}

    def test_run_without_nodes_raises_config_error(self):
        app = Agent()

        with pytest.raises(NodexConfigError):
            app.run()

    def test_node_failure_raises_nodex_node_error(self):
        app = Agent()

        @app.node(next="end")
        def broken(state):
            raise ValueError("boom")

        with pytest.raises(NodexNodeError):
            app.run()

    def test_middleware_runs_for_agent_nodes(self):
        app = Agent()
        calls = []

        @app.middleware
        def logger(state, next_node):
            calls.append("middleware")
            return next_node(state)

        @app.node(next="end")
        def start(state):
            calls.append("node")
            return {"ok": True}

        app.run()

        assert calls == ["middleware", "node"]
