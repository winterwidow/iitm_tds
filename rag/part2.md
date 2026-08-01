# Reranking:

## 1. Cross Encoder Rerankers:

Cross encoder encodes them together - the model sees the full interaction.

```python

from sentence_transformers import CrossEncoder

# Load a cross-encoder model
# ms-marco models are trained on MS MARCO passage ranking
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

query = "What is retrieval-augmented generation?"
candidates = [
    "RAG is a technique that combines retrieval and generation.",
    "The sky is blue on a clear day.",
    "Retrieval-Augmented Generation uses external documents to ground LLM answers.",
    "Python is a popular programming language.",
    "RAG reduces hallucination by providing factual context to language models.",
]

# Score all candidate pairs
scores = model.predict([(query, doc) for doc in candidates])

# Sort by score descending
ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

print("Reranked results:")
for rank, (doc, score) in enumerate(ranked, 1):
    print(f"  {rank}. [{score:.3f}] {doc}")

```

## 2. Cohere Rerank API:

Offers a managed reranker API - no GPU needed, great quality.

```python

import cohere

co = cohere.Client("YOUR_COHERE_API_KEY")

query = "What are the best practices for chunking in RAG?"
documents = [
    "Fixed-size chunking splits documents by character count.",
    "Semantic chunking groups sentences by topic similarity.",
    "Chunk overlap prevents information loss at boundaries.",
    "Parent-child chunking retrieves small chunks but returns large parents.",
    "Header-based chunking preserves document structure.",
]

response = co.rerank(
    model="rerank-english-v3.0",
    query=query,
    documents=documents,
    top_n=3,
    return_documents=True,
)

print("Cohere Reranked:")
for result in response.results:
    print(f"  Rank {result.index + 1}: [{result.relevance_score:.4f}] {result.document.text}")
```

## 3. FlashRankl - Fast local reranker:

Lightweight rereanker that runs on CPU, no API costs.

## 4. ColBERT — Late Interaction Reranking#

ColBERT encodes query and document into per-token vectors, then computes interaction via MaxSim. More accurate than cross-encoders but also heavier.

# 