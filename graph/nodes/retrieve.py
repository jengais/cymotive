from sentence_transformers import SentenceTransformer

# Load model once outside the node to avoid reloading every time
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

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
        desc = res['metadata'].get('description', '')
        mitigation = res['metadata'].get('mitigation', '')
        context_list.append(f"Past Incident: {desc}\nHistorical Mitigation: {mitigation}")
    
    return {"context": context_list}