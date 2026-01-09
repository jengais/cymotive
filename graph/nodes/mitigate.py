import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from utils.state import AgentState

def suggest_mitigation(state: AgentState):
    """
    Suggests a step-by-step mitigation plan based on the incident summary.
    """
    
    # 1. Initialize Gemini 2.5 Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2  # Slightly higher for creative problem solving
    )

    # 2. Extract the summary created by the previous node
    summary = state.get("summary", "No summary available.")

    # 3. Create the Mitigation Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an Incident Commander. Based on a technical summary, "
            "provide a prioritized list of mitigation steps. "
            "Categorize them into: Immediate Containment, Eradication, and Recovery."
        )),
        ("human", (
            "INCIDENT SUMMARY:\n{summary}\n\n"
            "Provide a bulleted mitigation plan."
        ))
    ])

    # 4. Chain and Invoke
    chain = prompt_template | llm
    response = chain.invoke({"summary": summary})

    # 5. Return the final update
    return {"mitigation": response.content}