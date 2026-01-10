import os
from langchain_core.prompts import ChatPromptTemplate
from utils.state import AgentState

from utils.start_all_models import llm_summarize

async def summarize_report(state: AgentState):
    """
    Summarizes the incident by combining the user's report with 
    technical context retrieved from the knowledge base.
    """
    
    # 2. Extract data from state
    report = state.get("report", "No report provided.")
    # Context is usually a list of strings from your 'retrieve' node
    context = "\n".join(state.get("context", []))

    # 3. Define the Prompt Template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Site Reliability Engineer (SRE). "
            "Your task is to create a concise technical summary of an incident. "
            "Use the 'Retrieved Context' to add technical depth (server names, "
            "error codes, or known fix patterns) to the 'User Report'."
        )),
        ("human", (
            "USER REPORT:\n{report}\n\n"
            "RETRIEVED CONTEXT:\n{context}\n\n"
            "Provide a 3-sentence technical summary including "
            "the likely root cause and the immediate impact."
        ))
    ])

    # 4. Create the chain and invoke
    chain = prompt_template | llm_summarize
    response = await chain.ainvoke({"report": report, "context": context})

    # 5. Return the update for LangGraph state
    return {"summary": response.content}