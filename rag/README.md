# RAG

## 1. FAISS -  Facebook AI Similarity Search

FAISS performs nearest neighbour search on high dimensional vectors (embeddings). This same concept is used in RAG.

The question FAISS answers is "which stored vector is most similar to my query".

``` 
import faiss
import numpy
```

- numpy is used for creating vectors.
- faiss indexes the vectors and performs similarity search.

```
d = 1536
n = 10001
```

- d - number of dimensions in each vector.
- n - number of vectors.

so the shape of the matrix would be `` (1000, 1536) ``.

FAISS requires vectors to be stored as 32 bit floating point values. 

```
index = faiss.IndexFlatL2(d)
```

This creates a FlatIndex
- Flat: store every vector, no compression, no approximation.
- L2 Index: compute the euclidean distance between 2 vector points.

We are measuring `` euclidean disance ``to understand the similarity of the search - how close two vectors are.

Other similarity measures:

1. Euclidean Distance: Straight line distance.
2. Inner Product: Larger value = more similar ---- Most retrieval systems.
3. Cosine Similarity: Measures the angle between two vectors --- Mostly used for test embeddings.

Cosine Similarity is used because it tells the direction of vectors. In text embeddings, directions capture the semantic meaning better than magnitude.

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

```
distances, indices = index.search(query, k=5)
```
- FAISS creates `` distance(query, vector)`` and sorts them.
- `` k = 5 `` gives the 5 closest vectors.

### Overall Workflow:
 
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