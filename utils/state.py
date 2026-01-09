# 1. Define the State


from typing import List, TypedDict


class AgentState(TypedDict):
    report: str
    summary: str
    mitigation: str
    context: List[str]  # Retrieved from Pinecone