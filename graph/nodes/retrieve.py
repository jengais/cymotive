
import asyncio
from dotenv import load_dotenv
# loads the variables into the environment
load_dotenv()
from pinecone_text.hybrid import hybrid_convex_scale

from utils.state import AgentState
from utils.start_all_models import embed_model, index, bm25_encoder


async def retrieve_node(state: AgentState):

    # Embed the user's incident report locally
    query_text = state["report"]
    sparse_vector = bm25_encoder.encode_queries(query_text)
    query_embedding = await asyncio.to_thread(embed_model.encode, query_text)
    query_embedding = query_embedding.tolist()

    
    # Use the utility to scale them (alpha 1.0 = pure dense, 0.0 = pure sparse)
    # This returns (scaled_dense, scaled_sparse)
    hdense, hsparse = hybrid_convex_scale(query_embedding, sparse_vector, alpha=0.7)

    # 3. Query Pinecone
    results = await asyncio.to_thread(
        index.query, 
        vector=hdense, 
        sparse_vector=hsparse, 
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