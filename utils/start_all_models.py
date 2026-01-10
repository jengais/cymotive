import os
from dotenv import load_dotenv
# loads the variables into the environment
load_dotenv()


from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder

# Load the pre-trained rules
bm25_path = "ingestion/bm25_values.json"

if os.path.exists(bm25_path):
    bm25_encoder = BM25Encoder().load(bm25_path)
else:
    print(f"⚠️ Warning: {bm25_path} not found. Hybrid search might fail.")

# Initialize Gemini 2.5 Flash
llm_summarize = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0 # For consistent, factual summaries
    )

    
# Initialize Gemini 2.5 Flash
llm_mitigate = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2  # Slightly higher for creative problem solving
    )

# Load model once outside the node to avoid reloading every time
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Setup Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = os.getenv("VEC_INDEX_NAME")
index = pc.Index(index_name)


print("\n✅ Project models and Pinecone index initialized successfully.")