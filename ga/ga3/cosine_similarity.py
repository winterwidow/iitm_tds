import json
import numpy as np

# Load JSON
with open("q-cosine-similarity-server.json", "r") as f:
    data = json.load(f)

documents = data["documents"]
queries = data["queries"]

# Extract document IDs and embeddings
doc_ids = [doc["doc_id"] for doc in documents]
doc_embeddings = np.array([doc["embedding"] for doc in documents])

results = {}

for query in queries:
    qid = query["query_id"]
    q_emb = np.array(query["embedding"])

    # Cosine similarity (embeddings are already normalized)
    sims = doc_embeddings @ q_emb

    # Sort by similarity descending, then doc_id ascending
    ranked = sorted(zip(doc_ids, sims), key=lambda x: (-x[1], x[0]))

    results[qid] = [doc_id for doc_id, _ in ranked[:5]]

print(json.dumps(results, indent=2))
