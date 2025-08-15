from typing import List, Dict, Tuple
from PIL import Image
import imagehash, hashlib, json, os

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def phash_file(path: str) -> str:
    with Image.open(path) as im:
        return str(imagehash.phash(im))

def build_hash_meta(paths: List[str]) -> List[Dict]:
    out = []
    for p in paths:
        try:
            out.append({
                "path": p,
                "sha256": sha256_file(p),
                "phash": phash_file(p)
            })
        except Exception:
            continue
    return out

def hamming(a: str, b: str) -> int:
    # phash hex strings -> int bits
    return bin(int(a, 16) ^ int(b, 16)).count("1")
