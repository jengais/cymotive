import os
from dotenv import load_dotenv
# loads the variables into the environment
load_dotenv()


from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


    # 1. Initialize Gemini 2.5 Flash
    # We use temperature=0 for consistent, factual summaries
llm_summarize = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )

    
    # 1. Initialize Gemini 2.5 Flash
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
index_name = "cyber-copilot-incidents"
index = pc.Index(index_name)


print("✅ Project models and Pinecone index initialized successfully.")