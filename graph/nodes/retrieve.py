
import asyncio
from dotenv import load_dotenv
# loads the variables into the environment
load_dotenv()

from utils.state import AgentState
from utils.start_all_models import embed_model, index



async def retrieve_node(state: AgentState):

    # Embed the user's incident report locally
    query_text = state["report"]
    query_embedding = await asyncio.to_thread(embed_model.encode, query_text)
    query_embedding = query_embedding.tolist()
    
    # Query Pinecone (ensure index was created with dim=384)
    results = await asyncio.to_thread(
        index.query, 
        vector=query_embedding, 
        top_k=2, 
        include_metadata=True
    )

    # Format the retrieved context for the LLM
    context_list = []
    for res in results['matches']:
        desc = res['metadata'].get('Incident Description', '')
        mitigation = res['metadata'].get('Mitigation Strategy', '')
        category = res['metadata'].get('category', '')

        context_list.append(f"Past Incident: {desc}\nHistorical Mitigation: {mitigation}\nCategory: {category}")
    
    return {"context": context_list}