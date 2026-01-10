# Cybersecurity Copilot: PoC Solution Report

## 1. Solution Design & Architecture
[cite_start]The Cybersecurity Copilot is a **Retrieval-Augmented Generation (RAG)** pipeline managed by a state-aware agentic framework using **LangGraph**[cite: 6, 13].

### High-Level Workflow:
* [cite_start]**Ingestion:** Security incident reports are chunked using `RecursiveCharacterTextSplitter`[cite: 11]. [cite_start]These chunks are converted into 384-dimensional dense vectors using the **`all-MiniLM-L6-v2`** SentenceTransformer model and stored in a **Pinecone** index[cite: 13, 37, 39].
* [cite_start]**Hybrid Search:** To ensure high precision, the system utilizes hybrid search, combining semantic dense vectors with sparse BM25 vectors to capture both conceptual context and specific technical keywords like "PostgreSQL" or "504 error"[cite: 14].
* **State Management:** An `AgentState` object tracks the report, retrieved context, generated summary, and mitigation plan throughout the lifecycle.
* **Nodes & Logic:**
    1.  [cite_start]**Retrieve:** Queries the Pinecone index for the top-2 relevant past incidents[cite: 38].
    2.  [cite_start]**Summarize:** An SRE persona merges the new report with historical context using few-shot examples[cite: 11].
    3.  [cite_start]**Mitigate:** An Incident Commander persona uses Chain-of-Thought (CoT) reasoning to create a prioritized NIST-aligned plan[cite: 12].

### Design Decisions & Trade-offs:
* [cite_start]**Model Choice:** **Gemini 2.0 Flash** was selected for its high speed, low latency, and massive context window, allowing for processing of large technical logs without truncation[cite: 4, 30].
* [cite_start]**Scalability:** The use of a vector database (Pinecone) ensures the knowledge base can grow from a dummy set of 10-20 incidents to thousands of historical logs without a linear increase in latency[cite: 37, 39].

---

## 2. Prompt Engineering
[cite_start]The system uses specialized prompts to ensure technical accuracy and actionable outputs[cite: 21].

### Summarization Node (Few-Shot)
* [cite_start]**Technique:** **Few-Shot Prompting**[cite: 23].
* **Implementation:** The system message includes concrete examples of raw reports and their ideal technical summaries. [cite_start]This "guides" the model to maintain a consistent tone and prioritize technical depth (server names, error codes) found in the retrieved context[cite: 22, 23].

### Mitigation Node (Chain-of-Thought)
* **Technique:** **Chain-of-Thought (CoT)**.
* **Implementation:** The prompt instructs the model to "think step-by-step" and analyze the primary threat vector before providing the plan. [cite_start]This ensures the remediation steps are prioritized into Immediate Containment, Eradication, and Recovery[cite: 12, 23].

### Edge Case Handling
* **Incomplete Reports:** The prompts are designed to be diagnostic. [cite_start]If a report is noisy or incomplete, the model is instructed to identify the "likely" root cause based on available symptoms (e.g., correlating high IOPS with a batch job) rather than failing[cite: 23].

---

## 3. Evaluation & Monitoring with LangSmith
[cite_start]To meet production standards, **LangSmith** is used for end-to-end observability and evaluation[cite: 41, 44].

* [cite_start]**Performance Monitoring:** We utilize LangSmith traces to inspect the full execution path, identifying latency bottlenecks and pinpointing where specific nodes might fail[cite: 44].
* **The RAG Triad Evaluation:**
    1.  [cite_start]**Groundedness:** Verifying that the summary only uses information from the report or context[cite: 42].
    2.  [cite_start]**Context Relevance:** Ensuring retrieved Pinecone matches are actually helpful for the specific incident[cite: 42].
    3.  [cite_start]**Answer Relevance:** Checking if mitigation steps accurately address the detected root cause[cite: 42].
* [cite_start]**Cost Awareness:** LangSmith tracks exact token usage per run[cite: 43]. [cite_start]With **Gemini 2.0 Flash**, a single run costs approximately **$0.00045**, making the solution highly cost-effective for large-scale enterprise use[cite: 43].

---

## 4. Sample Output
[cite_start]**Model:** Gemini 2.0 Flash [cite: 30]

[cite_start]**Input Report:** *"The payment-gateway service is throwing 504 Gateway Timeout errors for all checkout attempts. Latency spikes started appearing in the US-East-1 region after the 7:00 PM deployment."* [cite: 29]

**Copilot Output:**
* **Summary:** The `payment-gateway` service in `US-East-1` is experiencing widespread checkout failures due to 504 Gateway Timeouts following a 19:00 deployment. [cite_start]The root cause is likely a misconfigured rate-limiting mechanism in the new build, leading to gateway resource exhaustion[cite: 34].
* **Mitigation Plan:**
    1.  [cite_start]**Containment:** Immediately rollback the 7:00 PM deployment[cite: 34].
    2.  **Eradication:** Analyze deployment artifacts for traffic-shaping misconfigurations.
    3.  **Recovery:** Monitor P95 latency and error rates post-rollback before clearing the incident.