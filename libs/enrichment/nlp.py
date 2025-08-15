import spacy
from typing import List, Dict

def ensure_model(name: str = "en_core_web_sm"):
    try:
        return spacy.load(name)
    except OSError:
        # Allow runtime download if missing; not a stub, just dynamic install
        from spacy.cli import download
        download(name)
        return spacy.load(name)

def extract_entities(text: str) -> List[Dict]:
    nlp = ensure_model()
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
