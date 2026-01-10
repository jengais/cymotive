
from langgraph.graph import StateGraph, START, END

from utils.state import AgentState
from graph.nodes.retrieve import retrieve_node
from graph.nodes.summarize import summarize_report
from graph.nodes.mitigate import suggest_mitigation


# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("summarize", summarize_report)
workflow.add_node("mitigate", suggest_mitigation)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "summarize")
workflow.add_edge("summarize", "mitigate")
workflow.add_edge("mitigate", END)

app = workflow.compile()
