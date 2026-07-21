import json
import re
import math
import numpy as np
from rank_bm25 import BM25Okapi

# --------------------------
# Load files
# --------------------------

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\documents.jsonl", encoding="utf-8") as f:
    documents = [json.loads(line) for line in f]

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\chunk_rules.json", "r") as f:
    rules = json.load(f)

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\chunk_embeddings.json", "r") as f:
    chunk_embeddings = json.load(f)

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\queries.json", "r") as f:
    queries = json.load(f)

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\query_embeddings.json", "r") as f:
    query_embeddings = json.load(f)

chunk_size = rules["chunk_size"]
overlap = rules["overlap"]
rrf_k = rules["rrf_k"]
top_k = rules["top_k"]

# --------------------------
# Sentence splitter
# EXACTLY as instructed
# --------------------------


def split_sentences(text):
    s = re.split(r"[.!?]\s+", text.strip())
    return [x.strip() for x in s if x.strip()]


# --------------------------
# Create chunks
# --------------------------

chunks = []

global_chunk = 0

for doc in documents:

    doc_id = doc["doc_id"]
    sentences = split_sentences(doc["text"])

    step = chunk_size - overlap

    for i in range(0, len(sentences), step):

        chunk_sentences = sentences[i : i + chunk_size]

        if not chunk_sentences:
            break

        chunk_text = " ".join(chunk_sentences)

        chunk_id = f"{doc_id}_CHUNK_{global_chunk:03d}"

        chunks.append({"chunk_id": chunk_id, "text": chunk_text})

        global_chunk += 1

        if i + chunk_size >= len(sentences):
            break

print("Chunks:", len(chunks))

# --------------------------
# Ensure ordering matches embeddings
# --------------------------

embedding_keys = list(chunk_embeddings.keys())

assert len(embedding_keys) == len(chunks)

for c, k in zip(chunks, embedding_keys):
    if c["chunk_id"] != k:
        print("Mismatch!")
        print(c["chunk_id"], k)
        break

# --------------------------
# BM25
# --------------------------

tokenized = [c["text"].split() for c in chunks]

bm25 = BM25Okapi(tokenized)

# --------------------------
# Embedding matrix
# --------------------------

chunk_vectors = np.array([chunk_embeddings[c["chunk_id"]] for c in chunks], dtype=float)

chunk_norms = np.linalg.norm(chunk_vectors, axis=1)

# --------------------------
# Retrieval
# --------------------------

results = {}

for q in queries:

    qid = q["query_id"]

    query_text = q["text"]

    qvec = np.array(query_embeddings[qid], dtype=float)

    qnorm = np.linalg.norm(qvec)

    # -------------------
    # BM25
    # -------------------

    bm_scores = bm25.get_scores(query_text.split())

    sparse_order = np.argsort(-bm_scores)

    sparse_rank = {}

    for r, idx in enumerate(sparse_order, start=1):
        sparse_rank[idx] = r

    # -------------------
    # Cosine
    # -------------------

    cosine = (chunk_vectors @ qvec) / (chunk_norms * qnorm)

    dense_order = np.argsort(-cosine)

    dense_rank = {}

    for r, idx in enumerate(dense_order, start=1):
        dense_rank[idx] = r

    # -------------------
    # RRF
    # -------------------

    scores = []

    for idx in range(len(chunks)):

        score = 1 / (rrf_k + sparse_rank[idx]) + 1 / (rrf_k + dense_rank[idx])

        scores.append((score, chunks[idx]["chunk_id"]))

    scores.sort(key=lambda x: (-x[0], x[1]))

    results[qid] = [cid for _, cid in scores[:top_k]]

# --------------------------
# Save
# --------------------------

with open("C:\\Users\\naija\\iitm\\iitm_tds\\ga\\ga4\\rag_Search_pipeline\\output.json", "w") as f:
    json.dump(results, f, indent=2)

print("Done")
