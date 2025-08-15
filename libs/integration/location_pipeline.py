from __future__ import annotations
import os, io, json, time, traceback
from typing import Dict, Any, Iterable, Optional, Tuple, List, Callable

from libs.geo.enrichment import GeoEnricher, build_geocoder_from_config, build_wifi_cell_resolvers, build_landmark_detector
from libs.geo.providers.ip_geo import IPGeoProvider
from libs.geo.cache import RedisCache
from libs.geo.storage import save_estimate_postgis

try:
    import yaml
except Exception:
    yaml = None

def load_config(path: str = "config/geo.yml") -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML not installed. pip install PyYAML")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_enricher(cfg: dict):
    cache = RedisCache(cfg["redis"]["url"]) if cfg.get("redis") else None
    geocoder_fn = build_geocoder_from_config(cfg.get("geocoders"), cache=cache)
    wifi_resolvers, cell_resolvers = build_wifi_cell_resolvers(cfg.get("wifi_cell"), cache=cache)
    ip_provider = None
    if cfg.get("ip_geo", {}).get("enabled") and cfg["ip_geo"].get("maxmind_mmdb_path"):
        ip_provider = IPGeoProvider(cfg["ip_geo"]["maxmind_mmdb_path"])
    lm = build_landmark_detector(cfg.get("landmarks"))
    # Image loader for EXIF
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    import io as _io
    def _load_image(img_bytes, img_path):
        if img_bytes: return Image.open(_io.BytesIO(img_bytes))
        if img_path:  return Image.open(img_path)
        raise ValueError("no image data")
    enricher = GeoEnricher(
        ip_provider=ip_provider,
        geocoder=geocoder_fn,
        image_loader=_load_image,
        wifi_resolvers=wifi_resolvers,
        cell_resolvers=cell_resolvers,
        landmark_detector=lm,
        video_frame_every_sec=cfg.get("video",{}).get("frame_every_sec",2),
        video_frame_limit=cfg.get("video",{}).get("frame_limit",8),
    )
    return enricher

def enrich_record(enricher: GeoEnricher, record: Dict[str, Any]) -> Dict[str, Any]:
    est = enricher.from_record(record)  # may be None
    out = dict(record)  # copy original
    if est:
        out.setdefault("location", {})
        out["location"].update({
            "lat": est.lat,
            "lon": est.lon,
            "radius_m": est.radius_m,
            "method": est.method,
            "signals": [s.__dict__ for s in est.signals],
        })
    return out

def save_location(cfg: dict, entity_type: str, entity_id: str, est) -> None:
    if not est: return
    save_estimate_postgis(
        dsn=cfg["storage"]["postgis_dsn"],
        entity_type=entity_type,
        entity_id=entity_id,
        estimate=est,
        h3_resolution=cfg["storage"].get("h3_resolution"),
    )

class Pipeline:
    """Generic integration pipeline.
    You should implement a Collector interface that yields dict records with fields:
      - id, entity_type, text, ip, image_path/image_bytes, video_path, wifi, cell, lat, lon, xmp_text
    This Pipeline will call the enricher and persist the location.
    """
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.enricher = build_enricher(cfg)

    def run(self, records: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        for rec in records:
            try:
                enriched = enrich_record(self.enricher, rec)
                # persist if we have an estimate
                if enriched.get("location", {}).get("lat") is not None:
                    est = self.enricher.from_record(rec)
                    save_location(self.cfg, rec.get("entity_type","item"), rec.get("id","unknown"), est)
                yield enriched
            except Exception as e:
                rec["_error"] = str(e)
                rec["_trace"] = traceback.format_exc(limit=2)
                yield rec
