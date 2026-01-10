import asyncio
from pinecone.exceptions import PineconeException
from utils.state import AgentState
from utils.start_all_models import embed_model, index, bm25_encoder
from pinecone_text.hybrid import hybrid_convex_scale

async def retrieve_node(state: AgentState):
    query_text = state.get("report", "")
    
    # 1. Safety Check: If no report, don't bother querying
    if not query_text:
        return {"context": ["No incident report provided to search for context."]}

    try:
        # 2. Local Processing (Sparse + Dense)
        sparse_vector = bm25_encoder.encode_queries(query_text)
        query_embedding = await asyncio.to_thread(embed_model.encode, query_text)
        query_embedding = query_embedding.tolist()

        # Hybrid Scaling
        hdense, hsparse = hybrid_convex_scale(query_embedding, sparse_vector, alpha=0.7)

        # 3. Pinecone Query with timeout/network protection
        results = await asyncio.to_thread(
            index.query, 
            vector=hdense, 
            sparse_vector=hsparse, 
            top_k=2, 
            include_metadata=True
        )

        # 4. Format results with safe dictionary getting
        context_list = []
        for res in results.get('matches', []):
            metadata = res.get('metadata', {})
            desc = metadata.get('Incident Description', 'N/A')
            mitigation = metadata.get('Mitigation Strategy', 'No historical mitigation found.')
            category = metadata.get('category', 'unknown')

            context_list.append(
                f"Past Incident: {desc}\n"
                f"Historical Mitigation: {mitigation}\n"
                f"Category: {category}"
            )
        
        # If no matches were found, return a helpful note
        if not context_list:
            context_list = ["No relevant historical incidents found in the knowledge base."]

        return {"context": context_list}

    except PineconeException as pe:
        print(f"🌐 Pinecone API Error: {pe}")
        return {"context": ["Error connecting to the knowledge base. Proceeding with report data only."]}
    except Exception as e:
        print(f"💥 General Error in retrieve_node: {e}")
        return {"context": ["Context retrieval failed due to an internal error."]}