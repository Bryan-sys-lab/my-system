from typing import Tuple
import numpy as np

from .faiss_adapter import build_index as _build_index, search as _search


def build_index(vectors: np.ndarray):
    """Build a FAISS-compatible index (or the fallback) for `vectors`.

    Returns an index object suitable for passing to `search()`.
    """
    return _build_index(vectors)


def search(index, queries: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    return _search(index, queries, k=k)
