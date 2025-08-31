"""Adapter for open_clip to allow lazy imports and test fakes.

Provides create_model_and_transforms and get_tokenizer wrappers that use the
real `open_clip` when available, otherwise returns no-op placeholders.
"""
from typing import Any, Tuple


def create_model_and_transforms(model_name: str, pretrained: str = 'openai') -> Tuple[Any, Any, Any]:
    try:
        import open_clip  # type: ignore
        return open_clip.create_model_and_transforms(model_name, pretrained=pretrained, device='cpu')
    except Exception:
        # Return (None, None, identity_preprocess)
        def _noop(x):
            return x
        return None, None, _noop


def get_tokenizer(model_name: str):
    try:
        import open_clip  # type: ignore
        return open_clip.get_tokenizer(model_name)
    except Exception:
        return lambda texts: texts
