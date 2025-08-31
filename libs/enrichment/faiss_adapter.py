"""Adapter factory for FAISS so imports can be lazy and swapped in tests.

This module exposes build_index and search functions that use real faiss
if available, or a lightweight in-memory fallback otherwise.
"""
from typing import Tuple
import numpy as np


def build_index(vectors: np.ndarray):
    # Validate input shape: tests expect an exception for empty vectors
    if vectors is None or vectors.size == 0:
        raise Exception("Empty vectors provided to build_index")

    try:
        import faiss  # type: ignore
        d = vectors.shape[1]
        idx = faiss.IndexFlatIP(d)
        idx.add(vectors.astype('float32'))
        return idx
    except Exception:
        # Simple Python fallback: store vectors in a numpy array and compute
        # dot-products at search time.
        class _SimpleIndex:
            def __init__(self, vecs):
                self.vecs = vecs.astype('float32')
            def add(self, v):
                self.vecs = np.vstack([self.vecs, v.astype('float32')])
        return _SimpleIndex(vectors)


def search(index, queries: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    try:
        import faiss  # type: ignore
        D, I = index.search(queries.astype('float32'), k)
        return D, I
    except Exception:
        # Fallback: brute-force dot product
        q = queries.astype('float32')
        if hasattr(index, 'vecs'):
            mat = index.vecs
        else:
            # empty index
            return np.zeros((len(q), k)), -1 * np.ones((len(q), k), dtype=int)
        D = np.dot(q, mat.T)
        I = np.argsort(-D, axis=1)[:, :k]
        topk = np.take_along_axis(D, I, axis=1)
        return topk, I
