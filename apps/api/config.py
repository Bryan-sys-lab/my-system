"""
Configuration constants for the B-Search API
"""
import os
from typing import Optional

# Application settings
APP_TITLE = "b-search API"
APP_VERSION = "1.0.0"

# Environment variables helpers. We intentionally avoid binding SKIP_HEAVY_DEPS
# and DATA_DIR as fixed globals so tests that patch os.environ and then import
# this module will observe the patched values. Module-level __getattr__ below
# computes these on demand for "from ... import NAME" style imports.
def _read_skip_heavy_deps() -> bool:
	return os.environ.get("SKIP_HEAVY_DEPS", os.getenv("SKIP_HEAVY_DEPS", "0")) == "1"

def _read_data_dir() -> str:
	return os.environ.get(
		"DATA_DIR",
		os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", ".data")),
	)

def _faiss_dir_for(data_dir: str) -> str:
	return os.path.join(data_dir, "faiss")

def _index_path_for(faiss_dir: str) -> str:
	return os.path.join(faiss_dir, "images.index")

def _meta_path_for(faiss_dir: str) -> str:
	return os.path.join(faiss_dir, "images_meta.json")

# Label Studio configuration
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN", "")

# Run all secret
RUN_ALL_SECRET = os.getenv("RUN_ALL_SECRET")

# Default values
DEFAULT_NITTER_INSTANCE = "https://nitter.net"
DEFAULT_YOLO_MODEL = "yolov8n.pt"
DEFAULT_CLIP_THRESHOLD = 0.25
DEFAULT_PHASH_HAMMING_MAX = 6
DEFAULT_SEARCH_K = 12
DEFAULT_MAX_RESULTS = 25
DEFAULT_LIMIT = 50
DEFAULT_PAGE_SIZE = 50
DEFAULT_TIMEOUT = 30
DEFAULT_COLLECTOR_TIMEOUT = 10.0
DEFAULT_COLLECTOR_WORKERS = 8
DEFAULT_COLLECTOR_RETRIES = 1

# Batch operation defaults
DEFAULT_BATCH_RSS_PACK = "feeds/east_africa.yaml"
DEFAULT_DEEPWEB_MAX_PAGES = 100
DEFAULT_ONION_MAX_PAGES = 50
DEFAULT_BATCH_LIMIT = 50

# Analytics defaults
DEFAULT_ANALYTICS_DAYS = 30
DEFAULT_ANOMALY_THRESHOLD = 2.0
DEFAULT_SENTIMENT_DAYS = 7
DEFAULT_TOPIC_CLUSTERS = 5
DEFAULT_PREDICTION_DAYS = 7

# AI analysis defaults
DEFAULT_AI_ANALYSIS_DAYS = 7
DEFAULT_AI_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_AI_MAX_LENGTH = 500

# Export defaults
DEFAULT_EXPORT_FORMAT = "json"
DEFAULT_EXPORT_DAYS = 30
DEFAULT_EXPORT_LIMIT = 10000

# Monitoring defaults
DEFAULT_WATCHER_INTERVAL = 3600  # 1 hour
DEFAULT_AI_WATCHER_INTERVAL = 300  # 5 minutes

# File paths
DEFAULT_LOCAL_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".data"))

# Ensure directories exist using current environment at import time.
_current_data = _read_data_dir()
_current_faiss = _faiss_dir_for(_current_data)
os.makedirs(_current_faiss, exist_ok=True)
os.makedirs(os.path.join(_current_data, "uploads"), exist_ok=True)

def __getattr__(name: str):
	# Provide dynamic attributes for consumers that import these names
	if name == 'SKIP_HEAVY_DEPS':
		return _read_skip_heavy_deps()
	if name == 'DATA_DIR':
		return _read_data_dir()
	if name == 'FAISS_DIR':
		return _faiss_dir_for(_read_data_dir())
	if name == 'INDEX_PATH':
		return _index_path_for(_faiss_dir_for(_read_data_dir()))
	if name == 'META_PATH':
		return _meta_path_for(_faiss_dir_for(_read_data_dir()))
	raise AttributeError(name)