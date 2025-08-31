import os
import sys
import types

# Test-time shim: when SKIP_HEAVY_DEPS=1 is set, inject fake lightweight
# modules for heavy optional dependencies so test collection can proceed.
if os.getenv("SKIP_HEAVY_DEPS") == "1":
    def _no_op(*a, **k):
        return None

    # torch shim as a module providing cuda and no_grad
    torch_mod = types.ModuleType('torch')
    class _Cuda:
        @staticmethod
        def is_available():
            return False
    torch_mod.cuda = _Cuda()

    def _no_grad():
        class _Ctx:
            def __enter__(self):
                return None
            def __exit__(self, exc_type, exc, tb):
                return False
        return _Ctx()
    torch_mod.no_grad = _no_grad
    sys.modules.setdefault('torch', torch_mod)

    # open_clip shim
    open_clip_mod = types.ModuleType('open_clip')
    def _create_model_and_transforms(*args, **kwargs):
        return (None, None, lambda x: x)
    def _get_tokenizer(*args, **kwargs):
        return lambda texts: texts
    open_clip_mod.create_model_and_transforms = _create_model_and_transforms
    open_clip_mod.get_tokenizer = _get_tokenizer
    sys.modules.setdefault('open_clip', open_clip_mod)

    # faiss shim with IndexFlatIP
    faiss_mod = types.ModuleType('faiss')
    class IndexFlatIP:
        def __init__(self, dim):
            self.dim = dim
        def add(self, vectors):
            return None
    faiss_mod.IndexFlatIP = IndexFlatIP
    sys.modules.setdefault('faiss', faiss_mod)

    # whisper shim for ASR module
    whisper_mod = types.ModuleType('whisper')
    class _WhisperModel:
        def transcribe(self, path):
            # return a structure compatible with downstream code
            return {"text": ""}
    def load_model(name='base'):
        return _WhisperModel()
    whisper_mod.load_model = load_model
    sys.modules.setdefault('whisper', whisper_mod)

    # spacy shim
    spacy_mod = types.ModuleType('spacy')
    spacy_mod.load = lambda *a, **k: types.SimpleNamespace()
    sys.modules.setdefault('spacy', spacy_mod)

    # pytesseract shim
    pytesseract_mod = types.ModuleType('pytesseract')
    pytesseract_mod.image_to_string = lambda *a, **k: ''
    sys.modules.setdefault('pytesseract', pytesseract_mod)

    # selenium shim: provide webdriver and Options to allow import-time
    # in collectors that optionally use selenium for rendering.
    selenium_mod = types.ModuleType('selenium')
    webdriver_mod = types.ModuleType('selenium.webdriver')
    class _Options:
        def __init__(self):
            self._args = []
        def add_argument(self, arg):
            self._args.append(arg)
    class _DummyDriver:
        def __init__(self, *a, **k):
            self.page_source = ''
        def get(self, url):
            self.page_source = f'<html><body>stubbed {url}</body></html>'
        def implicitly_wait(self, s):
            return None
        def quit(self):
            return None
    class _Webdriver:
        Chrome = lambda *a, **k: _DummyDriver()
    webdriver_mod.webdriver = _Webdriver()
    webdriver_mod.Chrome = lambda *a, **k: _DummyDriver()
    webdriver_mod.Options = _Options
    # chrome.options nested module
    chrome_mod = types.ModuleType('selenium.webdriver.chrome')
    options_mod = types.ModuleType('selenium.webdriver.chrome.options')
    options_mod.Options = _Options
    chrome_mod.options = options_mod
    webdriver_mod.chrome = chrome_mod
    selenium_mod.webdriver = webdriver_mod
    selenium_mod.webdriver.chrome = chrome_mod
    sys.modules.setdefault('selenium', selenium_mod)
    sys.modules.setdefault('selenium.webdriver', webdriver_mod)
    sys.modules.setdefault('selenium.webdriver.chrome', chrome_mod)
    sys.modules.setdefault('selenium.webdriver.chrome.options', options_mod)
    # Prefer the real httpx package if available; only install a shim when
    # httpx is not installed in the environment. FastAPI/Starlette expect
    # many internals from httpx, so prefer the real package.
    try:
        import httpx  # type: ignore
    except Exception:
        # httpx not available — provide a minimal shim
        httpx_mod = types.ModuleType('httpx')
        class _Response:
            def __init__(self, status_code=200, text='', content=b''):
                self.status_code = status_code
                self._text = text
                self.content = content
            @property
            def text(self):
                return self._text
            def json(self):
                import json
                try:
                    return json.loads(self._text)
                except Exception:
                    return None

        class _Request:
            def __init__(self, url=''):
                self.url = url

        httpx_mod.Response = _Response
        httpx_mod.Request = _Request
        httpx_mod.get = lambda *a, **k: _Response()
        # Minimal BaseTransport to allow starlette TestClient to subclass it
        class BaseTransport:
            def handle_request(self, request):
                return _Response()

        httpx_mod.BaseTransport = BaseTransport
        # Minimal Client class to satisfy starlette TestClient subclassing
        class Client:
            def __init__(self, *a, **k):
                pass
            def get(self, *a, **k):
                return _Response()
            def post(self, *a, **k):
                return _Response()
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False

        httpx_mod.Client = Client
        sys.modules.setdefault('httpx', httpx_mod)

    # yt_dlp shim for video collectors
    yt_mod = types.ModuleType('yt_dlp')
    class YoutubeDL:
        def __init__(self, opts=None):
            self.opts = opts or {}
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def extract_info(self, url, download=False):
            # Return an empty-ish structure compatible with downstream code
            return {"entries": []}
    yt_mod.YoutubeDL = YoutubeDL
    sys.modules.setdefault('yt_dlp', yt_mod)

    # celery shim for workers/tasks import-time
    celery_mod = types.ModuleType('celery')
    class _FakeApp:
        def __init__(self, *a, **k):
            # simple namespace to hold decorators
            self.on_after_configure = types.SimpleNamespace()
            # connect should be a decorator
            def _connect_decorator(fn):
                return fn
            self.on_after_configure.connect = _connect_decorator
        def task(self, *a, **k):
            def _decorator(fn):
                return fn
            return _decorator
    def _Celery(*a, **k):
        return _FakeApp()
    celery_mod.Celery = _Celery
    sys.modules.setdefault('celery', celery_mod)

    # prometheus_client shim
    prom_mod = types.ModuleType('prometheus_client')
    def start_http_server(port):
        return None
    class Gauge:
        def __init__(self, *a, **k):
            pass
        def set(self, v):
            return None
    # Keep a registry of created metric names so generate_latest can return
    # something meaningful for tests that assert metric names are present.
    prom_mod._metrics = set()

    class Counter:
        def __init__(self, name, *a, **k):
            # store the metric name so generate_latest can emit it
            try:
                prom_mod._metrics.add(name)
            except Exception:
                pass
        def labels(self, *a, **k):
            class _L:
                def inc(self):
                    return None
            return _L()

    def generate_latest():
        # Emit a tiny text-format payload that contains any registered metric
        lines = []
        for m in sorted(getattr(prom_mod, '_metrics', [])):
            lines.append(f"# HELP {m} autogenerated test metric")
            lines.append(f"# TYPE {m} counter")
            lines.append(f"{m} 0")
        return "\n".join(lines).encode('utf-8')

    CONTENT_TYPE_LATEST = 'text/plain; version=0.0.4; charset=utf-8'
    prom_mod.start_http_server = start_http_server
    prom_mod.Gauge = Gauge
    prom_mod.Counter = Counter
    prom_mod.generate_latest = generate_latest
    prom_mod.CONTENT_TYPE_LATEST = CONTENT_TYPE_LATEST
    sys.modules.setdefault('prometheus_client', prom_mod)
