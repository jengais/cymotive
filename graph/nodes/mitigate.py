
from langchain_core.prompts import ChatPromptTemplate
from utils.state import AgentState
from utils.start_all_models import llm_mitigate


async def suggest_mitigation(state: AgentState):
    """
    Suggests a step-by-step mitigation plan based on the incident summary.
    """

    # Extract the summary created by the previous node
    summary = state.get("summary", "No summary available.")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an Incident Commander. Before providing the mitigation plan, "
            "briefly analyze the summary to identify the primary threat vector. "
            "Then, use a step-by-step reasoning process to prioritize actions."
        )),
        ("human", (
            "INCIDENT SUMMARY:\n{summary}\n\n"
            "Think step-by-step and provide the prioritized plan in sections: "
            "1. Analysis, 2. Immediate Containment, 3. Eradication, 4. Recovery."
        ))
    ])

    # Chain and Invoke
    try:
        # The actual API call
        chain = prompt_template | llm_mitigate
        response = await chain.ainvoke({"summary": summary})
        return {"mitigation": response.content}
        
    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error in mitigation node: {e}")
        return {"mitigation": "⚠️ Failed to generate mitigation plan due to a technical error."}