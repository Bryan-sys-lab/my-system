from __future__ import annotations
from typing import Dict, Any, List, Optional, Callable, Tuple
from .types import GeoSignal, GeoEstimate
from .triangulation import fuse
from .providers.text_geo import parse_latlon, parse_in_city
from .providers.wifi_cell import GoogleGeolocationResolver, MLSResolver
from .providers.geocoders import NominatimGeocoder, MapboxGeocoder, GoogleGeocoder, ChainedGeocoder
from .providers.ip_geo import IPGeoProvider
from .providers.exif_geo import from_pillow_image as exif_from_image, parse_sidecar_xmp, extract_network_from_xmp
from .providers.video_meta_geo import ffprobe_json, extract_geotag_from_probe, extract_network_hints, sample_video_frames
from .providers.landmark_detect import LandmarkDetector

class GeoEnricher:
    """Normalizes multiple weak geo signals into a fused location estimate."""
    def __init__(
        self,
        ip_provider: Optional[IPGeoProvider] = None,
        geocoder: Optional[Callable[[str], Optional[Tuple[float, float]]]] = None,
        image_loader=None,
        wifi_resolvers: Optional[list] = None,
        cell_resolvers: Optional[list] = None,
        landmark_detector: Optional[LandmarkDetector] = None,
        video_frame_every_sec: int = 2,
        video_frame_limit: int = 8,
    ):
        self.ip_provider = ip_provider
        self.geocoder = geocoder
        self.image_loader = image_loader
        self.wifi_resolvers = wifi_resolvers or []
        self.cell_resolvers = cell_resolvers or []
        self.landmark_detector = landmark_detector
        self.video_frame_every_sec = video_frame_every_sec
        self.video_frame_limit = video_frame_limit

    def from_record(self, record: Dict[str, Any]) -> Optional[GeoEstimate]:
        signals: List[GeoSignal] = []
        extra_network: Dict[str, Any] = {}

        # 1) IP
        ip = record.get("ip")
        if ip and self.ip_provider:
            s = self.ip_provider.lookup(ip)
            if s: signals.append(s)

        # 2) EXIF (if an image is present or path provided)
        img_bytes = record.get("image_bytes")
        img_path = record.get("image_path")
        if self.image_loader and (img_bytes or img_path):
            try:
                img = self.image_loader(img_bytes, img_path)
                s = exif_from_image(img)
                if s: signals.append(s)
            except Exception:
                pass

        # 2b) Sidecar XMP if provided
        xmp_text = record.get("xmp_text")
        if isinstance(xmp_text, str) and xmp_text:
            s = parse_sidecar_xmp(xmp_text)
            if s: signals.append(s)
            hints = extract_network_from_xmp(xmp_text)
            extra_network.update(hints)

        # 3) Video metadata (path)
        video_path = record.get("video_path")
        frame_paths = []
        if video_path:
            meta = ffprobe_json(video_path)
            s = extract_geotag_from_probe(meta)
            if s: signals.append(s)
            hints = extract_network_hints(meta)
            extra_network.update(hints)

            # Landmark detection on sampled frames
            if self.landmark_detector:
                import tempfile, os, shutil
                tempdir = tempfile.mkdtemp(prefix="frames_")
                try:
                    frame_paths = sample_video_frames(video_path, tempdir, self.video_frame_every_sec, self.video_frame_limit)
                    for fp in frame_paths:
                        for ls in self.landmark_detector.detect_on_image(fp):
                            signals.append(ls)
                finally:
                    shutil.rmtree(tempdir, ignore_errors=True)

        # 4) Text mentions
        text = record.get("text", "")
        signals.extend(parse_latlon(text))

        city_mentions = parse_in_city(text)
        for cm in city_mentions:
            city = cm.meta.get("city")
            if city and self.geocoder:
                try:
                    latlon = self.geocoder(city)
                    if latlon:
                        lat, lon = latlon
                        cm.lat = lat; cm.lon = lon; cm.radius_m = 5000.0
                except Exception:
                    continue
            if cm.is_valid():
                signals.append(cm)

        # 5) Explicit numeric coordinates in record
        if record.get("lat") is not None and record.get("lon") is not None:
            signals.append(GeoSignal(source="manual", lat=float(record["lat"]), lon=float(record["lon"]), radius_m=50.0))

        # 6) Cell/WiFi resolvers, incorporating extra network hints
        wifi = record.get("wifi") or extra_network.get("wifi")
        if wifi:
            for r in self.wifi_resolvers:
                try:
                    s = r.resolve(wifi=wifi, cell=None)
                    if s: 
                        signals.append(s)
                        break
                except Exception:
                    continue

        cell = record.get("cell") or extra_network.get("cell")
        if cell:
            for r in self.cell_resolvers:
                try:
                    s = r.resolve(wifi=None, cell=cell)
                    if s:
                        signals.append(s)
                        break
                except Exception:
                    continue

        # 7) IP from hints
        ip2 = extra_network.get("ip")
        if ip2 and self.ip_provider:
            s = self.ip_provider.lookup(ip2)
            if s: signals.append(s)

        if not signals:
            return None

        return fuse(signals)

def build_geocoder_from_config(cfg, cache=None):
    if not cfg or not cfg.get("enabled", True):
        return None
    order = cfg.get("prefer_order", [])
    providers = []
    if "nominatim" in order and cfg.get("nominatim"):
        c = cfg["nominatim"]
        providers.append(NominatimGeocoder(
            base_url=c.get("base_url", "https://nominatim.openstreetmap.org/search"),
            email=c.get("email"),
            user_agent=c.get("user_agent", "b-search-geo/1.0"),
            cache=cache, ttl=cfg.get("cache_ttl_sec", 86400),
            rate_limit_per_sec=float(c.get("rate_limit_per_sec", 1.0))
        ))
    if "mapbox" in order and cfg.get("mapbox") and cfg["mapbox"].get("token"):
        providers.append(MapboxGeocoder(token=cfg["mapbox"]["token"], cache=cache, ttl=cfg.get("cache_ttl_sec", 86400)))
    if "google" in order and cfg.get("google") and cfg["google"].get("api_key"):
        providers.append(GoogleGeocoder(api_key=cfg["google"]["api_key"], cache=cache, ttl=cfg.get("cache_ttl_sec", 86400)))
    if not providers:
        return None
    chain = ChainedGeocoder(providers)
    return chain.geocode_city

def build_wifi_cell_resolvers(cfg, cache=None):
    wifi_list = []; cell_list = []
    if not cfg or not cfg.get("enabled", True):
        return wifi_list, cell_list
    order = cfg.get("prefer_order", [])
    from .providers.wifi_cell import GoogleGeolocationResolver, MLSResolver
    for name in order:
        if name == "google" and cfg.get("google") and cfg["google"].get("api_key"):
            res = GoogleGeolocationResolver(api_key=cfg["google"]["api_key"], cache=cache, ttl=cfg.get("cache_ttl_sec", 86400))
            wifi_list.append(res); cell_list.append(res)
        if name == "mls" and cfg.get("mls"):
            c = cfg["mls"]
            res = MLSResolver(base_url=c.get("base_url"), api_key=c.get("api_key"), cache=cache, ttl=cfg.get("cache_ttl_sec", 86400))
            wifi_list.append(res); cell_list.append(res)
    return wifi_list, cell_list

def build_landmark_detector(cfg) -> Optional[LandmarkDetector]:
    try:
        if not cfg or not cfg.get("enabled", False):
            return None
        index_dir = cfg.get("index_dir")
        threshold = float(cfg.get("threshold", 0.25))
        return LandmarkDetector(index_dir=index_dir, threshold=threshold)
    except Exception:
        return None
