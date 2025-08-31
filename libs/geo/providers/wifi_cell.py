# server/libs/geo/providers/wifi_cell.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
import requests
import hashlib
from ..types import GeoSignal
from ...common.config import CFG  # ✅ central config

def _hash_key(ns: str, payload: dict) -> str:
    import json
    return f"geo:{ns}:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

class GoogleGeolocationResolver:
    def __init__(self, api_key: Optional[str] = None, cache=None, ttl=86400):
        # Fallback to config if not explicitly passed
        self.api_key = api_key or CFG.GOOGLE_GEOLOCATION_API_KEY
        self.cache = cache
        self.ttl = ttl

    def resolve(self, wifi: Optional[List[dict]] = None, cell: Optional[dict] = None) -> Optional[GeoSignal]:
        payload: Dict[str, Any] = {}
        if wifi:
            payload["wifiAccessPoints"] = [
                {"macAddress": ap.get("bssid"), "signalStrength": ap.get("rssi")}
                for ap in wifi if ap.get("bssid")
            ]
        if cell:
            payload["cellTowers"] = [{
                "mobileCountryCode": cell.get("mcc"),
                "mobileNetworkCode": cell.get("mnc"),
                "locationAreaCode": cell.get("lac"),
                "cellId": cell.get("cid"),
            }]
        if not payload:
            return None

        key = _hash_key("google_geo", payload)
        if self.cache:
            cached = self.cache.get_json(key)
            if cached:
                return GeoSignal(**cached)

        try:
            url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_key}"
            r = requests.post(url, json=payload, timeout=6)
            if r.status_code == 200:
                j = r.json()
                loc = j.get("location", {})
                acc = j.get("accuracy", 200.0)
                sig = GeoSignal(
                    source="wifi" if wifi else "cell",
                    lat=float(loc.get("lat")),
                    lon=float(loc.get("lng")),
                    radius_m=float(acc),
                    meta={"provider": "google"}
                )
                if self.cache:
                    self.cache.set_json(key, sig.__dict__, ttl=self.ttl)
                return sig
        except Exception:
            return None
        return None

class MLSResolver:
    """Stub MLS resolver for environments without external MLS packages.

    This resolver intentionally returns None for lookups. Production code can
    replace or extend this with a full implementation.
    """
    def __init__(self, *args, **kwargs):
        pass

    def resolve(self, *args, **kwargs):
        return None
