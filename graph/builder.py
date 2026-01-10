from typing import TypedDict, List
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

# from IPython.display import Image, display

# # Replace 'app' with your compiled LangGraph object
# try:
#     # 1. Generate the graph logic
#     graph_representation = app.get_graph()
    
#     # 2. Convert to Mermaid PNG and display
#     # This uses the Mermaid.ink API to render the image
#     display(Image(graph_representation.draw_mermaid_png()))
    
#     # Optional: Save to a file for your PDF submission
#     with open("copilot_architecture.png", "wb") as f:
#         f.write(graph_representation.draw_mermaid_png())
        
# except Exception as e:
#     # Fallback if the Mermaid API is unreachable
#     print(f"Diagram generation failed: {e}")