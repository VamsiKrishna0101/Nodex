from langgraph.graph import END, START, StateGraph

from nodex.decorators import get_registry
from nodex.exceptions import NodexConfigError


def build_graph(entry_node: str):
    registry = get_registry()

    if not registry:
        raise NodexConfigError("No nodes registered. Use @node() decorator to register nodes.")

    if entry_node not in registry:
        raise NodexConfigError(f"Entry node '{entry_node}' not found in registry.")

    graph = StateGraph(dict)

    _add_nodes(graph, registry)
    _add_edges(graph, registry, entry_node)

    return graph.compile()


def _add_nodes(graph: StateGraph, registry: dict) -> None:
    for node_name, node_data in registry.items():
        graph.add_node(node_name, node_data["func"])


def _add_edges(graph: StateGraph, registry: dict, entry_node: str) -> None:
    graph.add_edge(START, entry_node)

    for node_name, node_data in registry.items():
        config = node_data["config"]
        route = node_data.get("route")

        if route:
            graph.add_conditional_edges(
                node_name,
                lambda state, r=route: r["if_true"] if r["condition"](state) else r["if_false"],
                {
                    route["if_true"]: route["if_true"],
                    route["if_false"]: route["if_false"],
                }
            )
        elif config.next == "end":
            graph.add_edge(node_name, END)
        else:
            graph.add_edge(node_name, config.next)
