from .asr_adapter import get_transcriber


def transcribe(path: str, model_name: str = "base"):
    """Transcribe audio at `path` using the configured transcriber.

    Uses `libs.enrichment.asr_adapter.get_transcriber()` which will return a
    whisper-backed implementation when available or a shim otherwise.
    """
    tr = get_transcriber()
    return tr.transcribe(path)
