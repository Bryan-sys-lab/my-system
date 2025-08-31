# Testing shim documentation

This file documents the runtime test-time shims used when `SKIP_HEAVY_DEPS=1` is set in the environment.

Why these exist
- Many optional features in this repo depend on heavy native libraries or external services (torch, faiss, whisper, tesseract, selenium, postgres, redis, etc.). To keep unit tests fast and deterministic in CI, we provide lightweight shims that emulate the minimal API surface required during test collection and many unit tests.

How to enable
- Set the environment variable before running tests:

```bash
export SKIP_HEAVY_DEPS=1
export PYTHONPATH=.
pytest
```

List of major shims and behavior
- `torch`: provides `cuda.is_available()` (returns False) and `no_grad()` context manager that is a no-op.
- `open_clip`: stubs `create_model_and_transforms` and `get_tokenizer` returning no-op functions.
- `faiss`: provides `IndexFlatIP` class with `add()` no-op.
- `whisper`: `load_model()` returns an object with `transcribe()` returning `{"text": ""}`.
- `spacy`: `load()` returns a dummy namespace.
- `pytesseract`: `image_to_string()` returns empty string.
- `selenium`: provides nested `selenium.webdriver.chrome.options.Options` and a dummy `Chrome` driver with `get()` and `page_source`.
- `httpx`: minimal `Response`, `Request`, `Client`, and `BaseTransport` to satisfy starlette TestClient.
- `yt_dlp`: `YoutubeDL.extract_info()` returns an object with empty `entries`.
- `celery`: returns a fake Celery app where `task` and `on_after_configure.connect` are no-ops.
- `prometheus_client`: basic `Counter` and `Gauge` types; `generate_latest()` emits registered metric names.

Recommended practices
- Keep unit tests focused and mark heavy integration tests with `@pytest.mark.integration` so CI can run them in the integration job that starts real services.
- When adding new code that uses optional heavy deps, prefer lazy imports or adapter factories to reduce import-time failures.

When to remove a shim
- Remove the shim entry or set `SKIP_HEAVY_DEPS=0` for runs intended to validate native integrations or when CI provides a VM/image with preinstalled native libs.

