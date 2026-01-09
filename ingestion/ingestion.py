
import pandas as pd
import os
from dotenv import load_dotenv

# This looks for a .env file and loads the variables into the environment
load_dotenv()

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# 1. Load your CSV
# Make sure the file is in the same directory or provide the full path
df = pd.read_csv("ingestion/dummy_incidents_set.csv") 

# 2. Setup Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "cyber-copilot-incidents"

# Create index if it doesn't exist (using 384 dims for MiniLM)
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# 3. Initialize the Embedding Model (Free/Local)
# This model runs on your CPU/GPU for free
model = SentenceTransformer('all-MiniLM-L6-v2')

# 4. Process and Upsert
vectors = []
for idx, row in df.iterrows():
    # Combine columns to create a rich semantic representation
    content_to_embed = f"Incident: {row['Incident Description']}"
    embedding = model.encode(content_to_embed).tolist()
    
    vectors.append({
        "id": str(row['ID']),
        "values": embedding,
        "metadata": {
            "Category": row['Category'],
            "Incident Description": row['Incident Description'],
            "Mitigation Strategy": row['Mitigation Strategy']
        }
    })

# Pinecone upsert (limit batches to 100 for safety)
index.upsert(vectors=vectors)
print(f"Successfully ingested {len(vectors)} incidents from CSV to Pinecone.")


# # vf
# # 1. Setup API Keys (use environment variables for security)
# PINECONE_API_KEY = "your-api-key"
# pc = Pinecone(api_key=PINECONE_API_KEY)

# # 2. Create Index (Free Tier)
# index_name = "cyber-incidents"
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=384, # Dimension for 'all-MiniLM-L6-v2'
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# index = pc.Index(index_name)

# # 3. Initialize Embedding Model (Free/Local)
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # 4. Prepare your 20 dummy incidents
# # (Using a few examples from the list I generated for you)
# incidents = [
#     {
#         "id": "inc-01",
#         "text": "Unauthorized frames detected on the powertrain CAN bus causing engine stalling.",
#         "mitigation": "Implement Message Authentication Codes (MAC) and hardware-based IDS."
#     },
#     {
#         "id": "inc-02",
#         "text": "Malicious firmware update bypassed signature verification due to expired root certificate.",
#         "mitigation": "Update certificate revocation lists and enforce HSM checks."
#     }
#     # ... add the rest of the 20 here
# ]

# # 5. Upsert to Pinecone
# vectors = []
# for item in incidents:
#     embedding = model.encode(item["text"]).tolist()
#     vectors.append({
#         "id": item["id"],
#         "values": embedding,
#         "metadata": {"text": item["text"], "mitigation": item["mitigation"]}
#     })

# index.upsert(vectors=vectors)
# print("Successfully uploaded 20 incidents to Pinecone.")