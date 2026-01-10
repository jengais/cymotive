
\# 🛠️ Installation & Setup Guide

This guide will walk you through the steps to set up the **\*\*Cybersecurity Copilot\*\*** prototype on your local machine.

\#\# 1\. Prerequisites  
Ensure you have the following installed:  
\* **\*\*Python 3.9+\*\***  
\* A **\*\*Google AI Studio\*\*** API Key (for Gemini 2.5 Flash)  
\* A **\*\*Pinecone\*\*** Account and API Key  
\* A **\*\*Git\*\*** client

\---

\#\# 2\. Clone the Repository  

git clone [\<your-repository-url\>  ](https://github.com/jengais/cymotive.git)
cd cymotive

## **3\. Set Up a Virtual Environment**

It is highly recommended to use a virtual environment to manage dependencies:

Bash

\# Create the environment  
python \-m venv venv

\# Activate it  
\# On Windows:  
venv\\Scripts\\activate  
\# On macOS/Linux:  
source venv/bin/activate

## **4\. Install Dependencies**

Install the required libraries, including LangChain, Pinecone, and SentenceTransformers:

Bash

pip install \-r requirements.txt

*Note: Ensure pinecone-text, langchain-google-genai, and langgraph are included in your requirements.*

## ---

**5\. Environment Variables**

Create a .env file in the root directory and add your credentials:

Plaintext

GEMINI\_API\_KEY=your\_google\_gemini\_key  
PINECONE\_API\_KEY=your\_pinecone\_key  
VEC\_INDEX\_NAME=cyber-copilot-incidents

## ---

**6\. Project Initialization & Ingestion**

Before running the AI assistant, you must initialize the knowledge base:

1. **Ingest Data:** Run the ingestion script to chunk the dummy incident set, generate embeddings (using all-MiniLM-L6-v2), and upsert them to Pinecone.  

2. **Verify BM25:** Ensure the ingestion/bm25\_values.json file has been created. This file is required for hybrid search.

## ---

**7\. Running the Copilot**

To process your security incident reports through the LangGraph pipeline:

Bash

python main.py

This script will load your sample CSV, run the parallel processing graph (Retrieve \-\> Summarize \-\> Mitigate), and output the results to your terminal or a results file.

## ---

**8\. Monitoring (Optional)**

To enable **LangSmith** for tracing and evaluation:

1. Sign up at [smith.langchain.com](https://smith.langchain.com).  
2. Add these to your .env:  
   Plaintext  
   LANGCHAIN\_TRACING\_V2=true  
   LANGCHAIN\_API\_KEY=your\_langsmith\_key  
   LANGCHAIN\_PROJECT="Cyber-Copilot-Assignment"

\*\*Would you like me to help you create a \`requirements.txt\` file that lists all the specific versions of the libraries you used?\*\*  
