import os
from dotenv import load_dotenv

# loads the variables into the environment
load_dotenv()

from utils.state import AgentState

from utils.start_all_models import embed_model, index



def retrieve_node(state: AgentState):
    # 1. Embed the user's incident report locally
    query_text = state["report"]
    query_embedding = embed_model.encode(query_text).tolist()
    
    # 2. Query Pinecone (ensure index was created with dim=384)
    results = index.query(
        vector=query_embedding, 
        top_k=2, 
        include_metadata=True
    )
    
    # 3. Format the retrieved context for the LLM
    context_list = []
    for res in results['matches']:
        desc = res['metadata'].get('Incident Description', '')
        mitigation = res['metadata'].get('Mitigation Strategy', '')
        category = res['metadata'].get('category', '')

        context_list.append(f"Past Incident: {desc}\nHistorical Mitigation: {mitigation}\nCategory: {category}")
    
    return {"context": context_list}