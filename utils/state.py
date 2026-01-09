# 1. Define the State


class AgentState(TypedDict):
    report: str
    summary: str
    mitigation: str
    context: List[str]  # Retrieved from Pinecone