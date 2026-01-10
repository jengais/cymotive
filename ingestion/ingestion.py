
import pandas as pd
import os
from itertools import islice
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Helper for batching
def chunks(iterable, batch_size=100):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, batch_size))
        if not chunk:
            break
        yield chunk

df = pd.read_csv("ingestion/dummy_incidents_set.csv")

# 1. SETUP CHUNKING
# chunk_size is in characters; overlap prevents cutting a sentence in half
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# 2. SETUP HYBRID MODELS
bm25_encoder = BM25Encoder()
bm25_encoder.fit(df['Incident Description'].tolist())
bm25_encoder.dump("ingestion/bm25_values.json")

model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. SETUP PINECONE
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("VEC_INDEX_NAME")
if index_name not in pc.list_indexes().names():
    pc.create_index(index_name, dimension=384, metric="dotproduct", 
                   spec=ServerlessSpec(cloud="aws", region="us-east-1"))
index = pc.Index(index_name)

# 4. PROCESS WITH CHUNKING
vectors = []
for _, row in df.iterrows():
    full_text = row['Incident Description']
    
    # Split the long description into smaller chunks
    text_chunks = text_splitter.split_text(full_text)
    
    for i, chunk in enumerate(text_chunks):
        # Create a unique ID for each chunk (e.g., "1#0", "1#1")
        chunk_id = f"{row['ID']}#{i}"
        
        dense_vec = model.encode(chunk).tolist()
        sparse_vec = bm25_encoder.encode_documents(chunk) # Important: encode_documents for ingestion
        
        vectors.append({
            "id": chunk_id,
            "values": dense_vec,
            "sparse_values": sparse_vec,
            "metadata": {
                "Category": row['Category'],
                "Incident Description": chunk, # Store the chunk text, not the full text
                "Mitigation Strategy": row['Mitigation Strategy'],
                "Original_ID": str(row['ID']) # Keep reference to original row
            }
        })

# 5. UPSERT IN BATCHES
for batch in chunks(vectors, batch_size=100):
    index.upsert(vectors=batch)

print(f"✅ Ingested {len(vectors)} chunks from {len(df)} incidents.")


# import pandas as pd
# import os
# from dotenv import load_dotenv
# # This looks for a .env file and loads the variables into the environment
# load_dotenv()

# from pinecone import Pinecone, ServerlessSpec
# from sentence_transformers import SentenceTransformer
# from pinecone_text.sparse import BM25Encoder

# # Load your CSV
# # Make sure the file is in the same directory or provide the full path
# df = pd.read_csv("ingestion/dummy_incidents_set.csv") 

# # Fit the encoder on your dummy data (Bonus)
# bm25_encoder = BM25Encoder()
# bm25_encoder.fit(df['Incident Description'].tolist())
# bm25_encoder.dump("ingestion/bm25_values.json") # Save the encoder for the retriever to use


# # Setup Pinecone
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# pc = Pinecone(api_key=PINECONE_API_KEY)
# index_name = os.getenv("VEC_INDEX_NAME")

# # Create index if it doesn't exist (using 384 dims for MiniLM)
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=384,
#         metric="dotproduct",  # MUST BE dotproduct for hybrid search
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# index = pc.Index(index_name)

# # Initialize the Embedding Model (Free/Local)
# # This model runs on your CPU/GPU for free
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Process and Upsert
# vectors = []
# for idx, row in df.iterrows():

#     # Combine columns to create a rich semantic representation
#     content_to_embed = f"Incident: {row['Incident Description']}"
#     embedding = model.encode(content_to_embed).tolist()
#     sparse_vec = bm25_encoder.encode_documents(row['Incident Description']) # Generates sparse values
    
#     vectors.append({
#         "id": str(row['ID']),
#         "values": embedding,
#         "sparse_values": sparse_vec,
#         "metadata": {
#             "Category": row['Category'],
#             "Incident Description": row['Incident Description'],
#             "Mitigation Strategy": row['Mitigation Strategy']
#         }
#     })

# # Pinecone upsert (limit batches to 100 for safety)
# index.upsert(vectors=vectors)
# print(f"Successfully ingested {len(vectors)} incidents from CSV to Pinecone.")
