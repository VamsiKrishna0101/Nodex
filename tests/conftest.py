import pytest

from nodex.decorators import reset_registry
from nodex.display import Display
from nodex.errors import ErrorHandler
from nodex.state import NodexState
from nodex.tracer import Tracer


@pytest.fixture(autouse=True)
def clean_nodex_registry():
    reset_registry()
    yield
    reset_registry()


@pytest.fixture
def state():
    s = NodexState()
    s.update({"query": "test query", "api_key": "sk-test"})
    return s


@pytest.fixture
def empty_state():
    return NodexState()


@pytest.fixture
def tracer():
    return Tracer(agent_name="test-agent")


@pytest.fixture
def display():
    return Display(debug=True)


@pytest.fixture
def error_handler(tracer, display):
    return ErrorHandler(tracer=tracer, display=display)


@pytest.fixture
def sample_output():
    return {"research_results": "some results", "confidence": 0.9}


@pytest.fixture
def sample_node():
    def research(state: NodexState) -> dict:
        return {"research_results": f"results for {state.get('query')}"}
    return research


@pytest.fixture
def failing_node():
    def broken(state: NodexState) -> dict:
        raise ValueError("Something went wrong")
    return broken


@pytest.fixture
def invalid_output_node():
    def bad_node(state: NodexState):
        return "this is not a dict"
    return bad_node
