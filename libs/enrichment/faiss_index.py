from typing import Tuple, List
import faiss
import numpy as np

def build_index(vectors: np.ndarray) -> faiss.IndexFlatIP:
    # vectors must be L2-normalized for IP to behave like cosine similarity
    d = vectors.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(vectors.astype('float32'))
    return index

def search(index: faiss.IndexFlatIP, queries: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    D, I = index.search(queries.astype('float32'), k)
    return D, I
