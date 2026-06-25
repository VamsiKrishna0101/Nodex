from nodex.tracer import Tracer
from nodex.types import NodeStatus


class TestTracer:
    def test_initial_state(self):
        tracer = Tracer("test-agent")
        assert tracer.agent_name == "test-agent"
        assert tracer.results == []

    def test_end_node_records_success(self):
        tracer = Tracer("test-agent")
        tracer.start_node("research")
        result = tracer.end_node("research", output={"data": "results"}, tokens=100)
        assert result.status == NodeStatus.SUCCESS
        assert result.node_name == "research"
        assert result.tokens == 100

    def test_record_error_records_failure(self):
        tracer = Tracer("test-agent")
        tracer.start_node("research")
        result = tracer.record_error("research", error="Something broke")
        assert result.status == NodeStatus.FAILURE
        assert result.error == "Something broke"

    def test_record_skip_records_skipped(self):
        tracer = Tracer("test-agent")
        result = tracer.record_skip("research")
        assert result.status == NodeStatus.SKIPPED

    def test_get_trace_returns_execution_trace(self):
        tracer = Tracer("test-agent")
        tracer.start_node("research")
        tracer.end_node("research", tokens=100)
        tracer.start_node("writer")
        tracer.end_node("writer", tokens=200)
        trace = tracer.get_trace()
        assert trace.agent_name == "test-agent"
        assert len(trace.results) == 2
        assert trace.total_tokens == 300

    def test_get_trace_success_is_false_on_failure(self):
        tracer = Tracer("test-agent")
        tracer.start_node("research")
        tracer.record_error("research", error="broke")
        trace = tracer.get_trace()
        assert not trace.success

    def test_calculate_cost(self):
        tracer = Tracer("test-agent")
        cost = tracer.calculate_cost(1000)
        assert cost == 0.002

    def test_reset_clears_results(self):
        tracer = Tracer("test-agent")
        tracer.start_node("research")
        tracer.end_node("research", tokens=100)
        tracer.reset()
        assert tracer.results == []
