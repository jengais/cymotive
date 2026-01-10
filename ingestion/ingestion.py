
import pandas as pd
import os
from itertools import islice
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone.exceptions import PineconeException

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

# SETUP CHUNKING
# chunk_size is in characters; overlap prevents cutting a sentence in half
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# SETUP HYBRID MODELS
bm25_encoder = BM25Encoder()
bm25_encoder.fit(df['Incident Description'].tolist())
bm25_encoder.dump("ingestion/bm25_values.json")

model = SentenceTransformer('all-MiniLM-L6-v2')

# SETUP PINECONE
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("VEC_INDEX_NAME")
if index_name not in pc.list_indexes().names():
    pc.create_index(index_name, dimension=384, metric="dotproduct", 
                   spec=ServerlessSpec(cloud="aws", region="us-east-1"))
index = pc.Index(index_name)

# PROCESS WITH CHUNKING
batch_limit = 100
current_batch = []

print("🚀 Starting ingestion...")

for _, row in df.iterrows():
    full_text = str(row['Incident Description'])
    if not full_text.strip(): continue

    try:
        text_chunks = text_splitter.split_text(full_text)
        
        for i, chunk in enumerate(text_chunks):
            chunk_id = f"{row['ID']}#{i}"
            
            # Generate vectors
            dense_vec = model.encode(chunk).tolist()
            sparse_vec = bm25_encoder.encode_documents(chunk)
            
            current_batch.append({
                "id": chunk_id,
                "values": dense_vec,
                "sparse_values": sparse_vec,
                "metadata": {
                    "Category": row['Category'],
                    "Incident Description": chunk,
                    "Mitigation Strategy": row['Mitigation Strategy'],
                    "Original_ID": str(row['ID'])
                }
            })

            # Upsert when batch is full
            if len(current_batch) >= batch_limit:
                try:
                    index.upsert(vectors=current_batch)
                    current_batch = [] # Reset batch
                except PineconeException as e:
                    print(f"⚠️ Pinecone Upsert Error: {e}")

    except Exception as e:
        print(f"❌ Error processing row {row['ID']}: {e}")

# Upsert any remaining vectors
if current_batch:
    index.upsert(vectors=current_batch)

print(f"✅ Ingestion complete.")
