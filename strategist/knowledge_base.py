import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load a lightweight, extremely fast local HuggingFace embedding model
# This converts our English runbooks into mathematical vectors (arrays of numbers)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Our SRE Knowledge Base (In a massive enterprise, these would be parsed Markdown files)
RUNBOOKS = [
    {
        "title": "Payment Gateway Chaos Outage",
        "content": "ERROR SIGNATURE: 'broken.flag detected'. DIAGNOSIS: This is a known chaos engineering fault where a dummy flag blocks the payment API. MITIGATION: Do not restart the container. You must immediately use the fix_container tool to delete the broken.flag file."
    },
    {
        "title": "High Memory Usage Restarts",
        "content": "ERROR SIGNATURE: 'OOMKilled'. DIAGNOSIS: Container ran out of memory. MITIGATION: Restart the container and notify the backend team."
    }
]

# Extract just the text content to embed
runbook_texts = [rb["content"] for rb in RUNBOOKS]

# 3. Convert the text into vectors
print("Initializing FAISS Vector Database...")
embeddings = embedder.encode(runbook_texts)

# 4. Build the FAISS Index (The actual vector database)
dimension = embeddings.shape[1] # Find out how long the vectors are (usually 384)
index = faiss.IndexFlatL2(dimension) # Create an index using L2 (Euclidean) distance
index.add(np.array(embeddings)) # Insert our runbooks into the database

def query_runbooks(search_text, k=1):
    """Embeds the LLM's search query and retrieves the most relevant runbook."""
    try:
        # Convert the LLM's search string into a vector
        query_vector = embedder.encode([search_text])
        
        # Search the FAISS index for the 'k' closest matches
        distances, indices = index.search(np.array(query_vector), k)
        
        # Return the text of the best match
        best_match_index = indices[0][0]
        return runbook_texts[best_match_index]
    except Exception as e:
        return f"Database Error: {str(e)}"