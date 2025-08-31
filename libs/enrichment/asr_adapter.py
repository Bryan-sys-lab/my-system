"""ASR adapter factory.

Provides a small abstraction so callers can obtain a transcriber without
import-time dependency on `whisper`.
"""
from typing import Protocol, Dict


class Transcriber(Protocol):
    def transcribe(self, path: str) -> Dict:
        ...


def _shim() -> Transcriber:
    class _Shim:
        def transcribe(self, path: str) -> Dict:
            return {"text": ""}
    return _Shim()


def get_transcriber() -> Transcriber:
    try:
        import whisper  # type: ignore

        class _WhisperWrapper:
            def __init__(self, model_name: str = "base"):
                self.model = whisper.load_model(model_name)

            def transcribe(self, path: str) -> Dict:
                return self.model.transcribe(path)

        return _WhisperWrapper()
    except Exception:
        return _shim()
