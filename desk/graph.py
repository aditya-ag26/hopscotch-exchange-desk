from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from desk.decision import escalate, policy_check, route_exit
from desk.investigator import after_investigator, make_investigator
from desk.reads import extract_claim, read_tone
from desk.respond import respond
from desk.state import DeskState


def build_graph(tools: list):
    graph = StateGraph(DeskState)

    graph.add_node("extract_claim", extract_claim)
    graph.add_node("read_tone", read_tone)
    graph.add_node("investigator", make_investigator(tools))
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("policy_check", policy_check)
    graph.add_node("escalate", escalate)
    graph.add_node("respond", respond)

    graph.add_edge(START, "extract_claim")
    graph.add_edge(START, "read_tone")

    graph.add_edge(["extract_claim", "read_tone"], "investigator")

    graph.add_conditional_edges("investigator", after_investigator)
    graph.add_edge("tools", "investigator")

    graph.add_conditional_edges("policy_check", route_exit)
    graph.add_edge("escalate", END)
    graph.add_edge("respond", END)

    return graph.compile()
