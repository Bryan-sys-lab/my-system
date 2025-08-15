from typing import List, Dict
import torch
import numpy as np
import open_clip
from PIL import Image

def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"

def build_clip(model_name: str = "ViT-B-32", pretrained: str = "openai"):
    model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained, device=_device())
    tokenizer = open_clip.get_tokenizer(model_name)
    return model, preprocess, tokenizer

def embed_images(image_paths: List[str], model_name: str = "ViT-B-32", pretrained: str = "openai"):
    model, preprocess, _ = build_clip(model_name, pretrained)
    dev = _device()
    vecs = []
    for p in image_paths:
        img = preprocess(Image.open(p).convert("RGB")).unsqueeze(0).to(dev)
        with torch.no_grad():
            feat = model.encode_image(img)
            feat = feat / feat.norm(dim=-1, keepdim=True)
        vecs.append(feat.squeeze(0).cpu().numpy())
    return np.vstack(vecs)

def embed_texts(texts: List[str], model_name: str = "ViT-B-32", pretrained: str = "openai"):
    model, _, tokenizer = build_clip(model_name, pretrained)
    dev = _device()
    toks = tokenizer(texts).to(dev)
    with torch.no_grad():
        feat = model.encode_text(toks)
        feat = feat / feat.norm(dim=-1, keepdim=True)
    return feat.cpu().numpy()
