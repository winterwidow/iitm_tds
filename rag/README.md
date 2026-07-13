# RAG

## 1. FAISS -  Facebook AI Similarity Search

FAISS performs nearest neighbpur search on high dimensional vectors (embeddings). This same concept is used in RAG.

``` 
import faiss
import numpy
```

- numpy is used for creating vectors.
- faiss indexes the vectors and performs similarity search

```
d = 1536
n = 10001
```

d - number of dimensions in each vector
n - number of vectors

so the shape of the matrix would be `` (1000, 1536) ``

