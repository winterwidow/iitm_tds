# RAG

## 1. FAISS - Facebook AI Similarity Search

FAISS performs nearest neighbour search on high dimensional vectors (embeddings). This same concept is used in RAG.

The question FAISS answers is "which stored vector is most similar to my query".

### 1. Module imports

```
import faiss
import numpy
```

- numpy is used for creating vectors.
- faiss indexes the vectors and performs similarity search.

### 2. Define the data

```
d = 1536
n = 10001
```

- d - number of dimensions in each vector.
- n - number of vectors.

so the shape of the matrix would be `(1000, 1536)`.

FAISS requires vectors to be stored as 32 bit floating point values.

### 3. Create an index

```
index = faiss.IndexFlatL2(d)
```

This creates a FlatIndex

- Flat: store every vector, no compression, no approximation.
- L2 Index: compute the euclidean distance between 2 vector points.

We are measuring `euclidean disance`to understand the similarity of the search - how close two vectors are.

Other similarity measures:

1. Euclidean Distance: Straight line distance.
2. Inner Product: Larger value = more similar ---- Most retrieval systems.
3. Cosine Similarity: Measures the angle between two vectors --- Mostly used for test embeddings.

Cosine Similarity is used because it tells the direction of vectors. In text embeddings, directions capture the semantic meaning better than magnitude.

### 4. Query and database creation

```
docs = [
    "Paris is the capital of France.",
    "Python is a programming language.",
    "Cats are mammals."
]
doc_vectors = embedding_model.encode(docs)
```

This is how a database of vectors would be created.

```
query = np.random.randn(1, d).astype("float32")
```

This is a dummy query created to search for the most similar vector in the database.

```
query_vector = embedding_model.encode(
    ["What is France's capital?"]
)
```

This is how an actual query from the user can be created and embedded.

### 5. Searching

```
distances, indices = index.search(query, k=5)
```

- FAISS creates ` distance(query, vector)` and sorts them.
- `k = 5` gives the 5 closest vectors.

### 6. Overall Workflow:

``
Generate vectors

        │

        ▼

Create FAISS Index

        │

        ▼

Add vectors

        │

        ▼

Generate query

        │

        ▼

Compute distance to every vector

        │

        ▼

Sort by smallest distance

        │

        ▼

Return top 5 nearest vectors
``

### 7. HNSW - Hierarchical Navigable Small World

This is another way of created an index instead of Flat Index.

```
M = 32          # number of connections per node
ef_construction = 200  # how carefully FAISS builds a graph

index = faiss.IndexHNSWFlat(d, M)  # create the index
index.hnsw.efConstruction = ef_construction # examine these many candidates before deciding best neighbour
index.add(vectors)

# At search time, set ef_search
index.hnsw.efSearch = 64 # how many neighbours of the node to explore
distances, indices = index.search(query, k=5) # give top 5 values
```

- higher `M` means better search accuracy, more memory.
- small `ef`: Fast indexing less accurate.
- large `ef`: Slower indexing, better graph.
- HNSW stores as a groah indeatd of list like FlatIndex.
- Search does not have to start at the first node - it can be any node - then moves to search the neighbours.

## 2. ChromaDB

ChromaDB wraps the entire vector-search pipeline. Instead of manually generating embeddings, creating a FAISS index, maintaining a mapping between vectors and documents, and implementing metadata filtering yourself, you work directly with text and metadata, while ChromaDB manages the embeddings, indexing, storage, and retrieval behind the scenes.

With FAISS, you had to:

- Generate embeddings yourself.
- Create the index.
- Store vectors.
- Store metadata separately.
- Search the index.

With ChromaDB, you simply provide text and it:

- generates embeddings,
- stores them,
- builds the index (HNSW by default),
- stores metadata,
- lets you filter by metadata.

## 3. PGVector

Works if PostgreSQL is set up - you can add a vector search without creating a new service.

# Chunking Strategies

1. Fixed size chunks
2. Sentence/Paragraph based chunks
3. Header based/markdown based chunks - split on markdown headers
4. Parent CHild chunks - Store large “parent” chunks for context, index small “child” chunks for retrieval. When a child chunk matches, return the parent.
5. Semantic Chunks - split when meaning shifts
6. Token based chunking - always chunk by tokens not characters (embedding models count tokens).

## Metadata to chunks:

Always add metadata to chunks, these can be used for citations later.

```
from langchain.schema import Document

def chunk_with_metadata(filepath: str, chunks: list[str]) -> list[Document]:
    docs = []
    for i, chunk in enumerate(chunks):
        docs.append(Document(
            page_content=chunk,
            metadata={
                "source": filepath,
                "chunk_id": i,
                "total_chunks": len(chunks),
            }
        ))
    return docs
```

## Problem with early chunking:

When you chunk a document before embedding, each chunk loses context from the rest of the document.

## Late Chunking

The traditional way is to chunk then embed. In late chunking, we first embed then chunk.

1. Pass the full document through the embedding model.
2. Get token level embeddings for every token .
3. Mean-pool token embeddings within each chunk’s span.

Each chunks embeddings now contains context from the full document.

Using Jina's Late Chunking API:

```
import requests

JINA_API_KEY = " "  # Get at jina.ai

def jina_late_chunk_embed(document: str, chunks: list[str]) -> list[list[float]]:
    """Use Jina's API for late chunking embeddings."""
    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "jina-embeddings-v3",
            "input": [
                {"text": document},           # Full document first
                *[{"text": c} for c in chunks]  # Then individual chunks
            ],
            "late_chunking": True,             # The magic flag
            "task": "retrieval.passage",
        }
    )

    data = response.json()
    # Skip the first embedding (full document), return chunk embeddings
    return [item["embedding"] for item in data["data"][1:]]

embeddings = jina_late_chunk_embed(document, chunks)
print(f"Received {len(embeddings)} embeddings from Jina API")
```

# Contextual Retrieval

Before embedding a chunk, prepend a short context sentence that describes where the chunk comes from and what it’s about — generated by a fast LLM using the full document as input. This technique was published by Anthropic.

```
import anthropic
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import Optional

client = anthropic.Anthropic()

def generate_chunk_context(
    full_document: str,
    chunk: str,
    model: str = "claude-haiku-4-5",
) -> str:
    """
    Use Claude to generate a context sentence for a chunk,
    given the full document.

    Uses prompt caching for the full document (major cost saving
    when processing many chunks from the same document).
    """
    response = client.beta.messages.create(
        model=model,
        max_tokens=200,
        system="You are a document analyzer. Given a document and a chunk from it, "
               "write 1-2 sentences of context that describe what the chunk is about "
               "and where it fits in the document. Be concise and specific.",
        messages=[
            {
                "role": "user",
                "content": [
                    # Full document with cache_control — this gets cached!
                    {
                        "type": "text",
                        "text": f"<document>\n{full_document}\n</document>",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"<chunk>\n{chunk}\n</chunk>\n\n"
                            "Write a brief context sentence for this chunk. "
                            "Return ONLY the context sentence, nothing else."
                        ),
                    },
                ],
            }
        ],
        betas=["prompt-caching-2024-07-31"],
    )

    return response.content[0].text.strip()

def contextual_chunk(
    full_document: str,
    chunk: str,
) -> str:
    """Prepend generated context to a chunk."""
    context = generate_chunk_context(full_document, chunk)
    return f"{context}\n\n{chunk}"

def build_contextual_vectorstore(
    documents: list[str],
    collection_name: str = "contextual_rag",
) -> Chroma:
    """
    Build a Chroma vectorstore using contextual retrieval.

    For each document:
    1. Split into chunks
    2. Generate context for each chunk (with caching)
    3. Prepend context + embed
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_docs = []

    for doc_idx, document in enumerate(documents):
        chunks = splitter.split_text(document)
        print(f"Document {doc_idx + 1}: {len(chunks)} chunks")

        for chunk_idx, chunk in enumerate(chunks):
            print(f"  Generating context for chunk {chunk_idx + 1}/{len(chunks)}...")
            contextualized = contextual_chunk(full_document=document, chunk=chunk)

            all_docs.append(Document(
                page_content=contextualized,
                metadata={
                    "doc_idx": doc_idx,
                    "chunk_idx": chunk_idx,
                    "original_chunk": chunk,  # keep original for display
                }
            ))

    print(f"\nBuilding vectorstore with {len(all_docs)} contextual chunks...")
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=OpenAIEmbeddings(),
        collection_name=collection_name,
    )
    print("Done!")
    return vectorstore

# Usage
documents = [
    """
    Acme Corporation Q3 2024 Earnings Report

    Financial Performance:
    Revenue reached $1.2 billion, representing 15% year-over-year growth.
    Operating income was $240 million, with margins expanding 200 basis points.

    Product Segment:
    The cloud division grew 42% to $450 million, now representing 37.5% of revenue.
    Hardware sales declined 8% to $320 million due to supply chain constraints.

    Outlook:
    Management raised full-year guidance to $4.8-5.0 billion in revenue.
    Q4 expected revenue: $1.4-1.5 billion.
    """,
]

vectorstore = build_contextual_vectorstore(documents)

# Query
results = vectorstore.similarity_search("What happened with cloud revenue?", k=3)
for r in results:
    print(f"\n--- Result ---")
    print(r.page_content[:300])

```

## Contextual Retrieval + Hybrid + Reranking

```
class AnthropicRAGStack:
    """
    Anthropic's full recommended RAG stack:
    1. Contextual chunking (semantic context injection)
    2. Hybrid search (dense + BM25)
    3. Reranking (cross-encoder)
    """
    def __init__(self, documents: list[str]):
        from rank_bm25 import BM25Okapi
        from sentence_transformers import CrossEncoder

        # Build contextual vectorstore (dense)
        self.vectorstore = build_contextual_vectorstore(documents)

        # Build BM25 index (sparse)
        self.all_chunks = []  # collect all chunks during indexing
        self.bm25 = BM25Okapi([c.lower().split() for c in self.all_chunks])

        # Reranker
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str, k: int = 5) -> list[str]:
        # 1. Dense retrieval
        dense = self.vectorstore.similarity_search(query, k=20)

        # 2. Sparse retrieval (BM25)
        scores = self.bm25.get_scores(query.lower().split())
        sparse_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:20]
        sparse = [self.all_chunks[i] for i in sparse_idx]

        # 3. Merge candidates
        candidates = list({d.page_content for d in dense} | set(sparse))

        # 4. Rerank
        pairs = [(query, c) for c in candidates]
        rerank_scores = self.reranker.predict(pairs)
        reranked = sorted(zip(candidates, rerank_scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in reranked[:k]]

```
