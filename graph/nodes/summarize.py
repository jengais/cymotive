
from langchain_core.prompts import ChatPromptTemplate
from utils.state import AgentState
from utils.start_all_models import llm_summarize



async def summarize_report(state: AgentState):
    """
    Summarizes the incident by combining the user's report with 
    technical context retrieved from the knowledge base.
    """
    
    # Extract data from state
    report = state.get("report", "No report provided.")
    context_list = state.get("context", [])
    context = "\n".join(context_list) if context_list else "No context available."


    SUMMARIZATION_EXAMPLES = """
    EXAMPLE 1:
    USER REPORT: System slow since 2pm. Database keeps restarting. Error code 500 in logs.
    RETRIEVED CONTEXT: Past Incident: DB OOM due to massive query. Historical Mitigation: Increase memory.
    SUMMARY: Technical summary: A Database Out-of-Memory (OOM) error caused repeated service restarts and 500-level errors starting at 14:00 UTC. The root cause is likely an unoptimized, massive query similar to past incidents. Immediate impact includes "100%" service unavailability during restart cycles.
    """

    # Inside summarize_report:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Site Reliability Engineer (SRE). "
            "Create concise 3-sentence technical summaries. "
            f"{SUMMARIZATION_EXAMPLES}"
        )),
        ("human", (
            "<report>{report}</report>\n"
            "<context>{context}</context>\n\n"
            "Generate a <summary> based on the above tags."
        ))
    ])

    try:
        # Chain and Invoke
        chain = prompt_template | llm_summarize
        
        # We use a timeout or safety check if needed
        response = await chain.ainvoke({"report": report, "context": context})

        # Return the summary
        return {"summary": response.content}

    except Exception as e:
        # Handle LLM or Prompt failures
        print(f"⚠️ Error in summarize_report: {e}")
        
        # Return a fallback summary so the next node (mitigation) still has something to work with
        fallback_summary = f"Technical summary unavailable. Original Report: {report[:100]}..."
        return {"summary": fallback_summary}