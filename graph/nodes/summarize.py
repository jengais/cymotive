import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from utils.state import AgentState

async def summarize_report(state: AgentState):
    """
    Summarizes the incident by combining the user's report with 
    technical context retrieved from the knowledge base.
    """
    
    # 1. Initialize Gemini 2.5 Flash
    # We use temperature=0 for consistent, factual summaries
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )

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
    chain = prompt_template | llm
    response = await chain.invoke({"report": report, "context": context})

    # 5. Return the update for LangGraph state
    return {"summary": response.content}