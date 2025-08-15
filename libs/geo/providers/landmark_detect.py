from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
import os, json

from ..types import GeoSignal

class LandmarkIndex:
    """Encapsulates a FAISS index of CLIP image/text embeddings.
    Expected layout in `index_dir`:
      - index.faiss
      - meta.jsonl  # lines: {"id":"eiffel_tower","name":"Eiffel Tower","lat":48.8583,"lon":2.2945}
    You can build this offline from Google Landmarks v2, Wikimedia, Mapillary, etc.
    """
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        self.index = None
        self.meta = []
        self._load()

    def _load(self):
        try:
            import faiss, numpy as np, json, os
            idx_path = os.path.join(self.index_dir, "index.faiss")
            meta_path = os.path.join(self.index_dir, "meta.jsonl")
            if os.path.exists(idx_path) and os.path.exists(meta_path):
                self.index = faiss.read_index(idx_path)
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.meta = [json.loads(line) for line in f if line.strip()]
        except Exception:
            self.index = None
            self.meta = []

    def search(self, vec, topk=5):
        try:
            import numpy as np
            if self.index is None:
                return []
            D, I = self.index.search(vec.astype("float32"), topk)
            out = []
            for score, idx in zip(D[0], I[0]):
                if idx < 0 or idx >= len(self.meta):
                    continue
                out.append((score, self.meta[idx]))
            return out
        except Exception:
            return []

class CLIPEncoder:
    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.preprocess = None
        self._init()

    def _init(self):
        try:
            import torch, clip
            self.device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
            self.model, self.preprocess = clip.load(self.model_name, device=self.device, download_root=os.environ.get("CLIP_CACHE","/tmp"))
        except Exception:
            self.model = None
            self.preprocess = None

    def encode_image(self, image_path: str):
        try:
            import torch, PIL.Image as Image, numpy as np
            if not self.model or not self.preprocess:
                return None
            img = Image.open(image_path).convert("RGB")
            with torch.no_grad():
                x = self.preprocess(img).unsqueeze(0).to(self.device)
                emb = self.model.encode_image(x)
                emb = emb / emb.norm(dim=-1, keepdim=True)
                return emb.cpu().numpy()
        except Exception:
            return None

class LandmarkDetector:
    def __init__(self, index_dir: Optional[str] = None, threshold: float = 0.25):
        self.encoder = CLIPEncoder()
        self.index = LandmarkIndex(index_dir) if index_dir else None
        self.threshold = threshold

    def detect_on_image(self, image_path: str) -> List[GeoSignal]:
        vec = self.encoder.encode_image(image_path)
        if vec is None or self.index is None:
            return []
        results = self.index.search(vec, topk=5)
        out: List[GeoSignal] = []
        for score, meta in results:
            # FAISS returns inner product distances if index is IP; treat score as similarity
            sim = float(score)
            if sim >= self.threshold and all(k in meta for k in ("lat","lon")):
                out.append(GeoSignal(
                    source="landmark_visual",
                    lat=float(meta["lat"]),
                    lon=float(meta["lon"]),
                    radius_m=100.0,  # typical landmark localization
                    meta={"id": meta.get("id"), "name": meta.get("name"), "similarity": sim}
                ))
        return out
