from __future__ import annotations
from typing import Optional, Tuple, Dict, Any, List
import time
import hashlib
import requests

def _hash_key(ns: str, q: str) -> str:
    return f"geo:{ns}:{hashlib.sha256(q.encode('utf-8')).hexdigest()}"

class BaseGeocoder:
    def __init__(self, cache=None, ttl=86400):
        self.cache = cache
        self.ttl = ttl

    def geocode_city(self, name: str) -> Optional[Tuple[float, float]]:
        raise NotImplementedError

class NominatimGeocoder(BaseGeocoder):
    def __init__(self, base_url: str, email: str, user_agent: str, cache=None, ttl=86400, rate_limit_per_sec: float = 1.0):
        super().__init__(cache, ttl)
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.user_agent = user_agent
        self.min_interval = 1.0 / max(rate_limit_per_sec, 0.1)
        self._last_time = 0.0

    def _sleep_rate(self):
        dt = time.time() - self._last_time
        wait = self.min_interval - dt
        if wait > 0:
            time.sleep(wait)
        self._last_time = time.time()

    def geocode_city(self, name: str) -> Optional[Tuple[float, float]]:
        key = _hash_key("nominatim", name.lower())
        if self.cache:
            cached = self.cache.get_json(key)
            if cached and "lat" in cached and "lon" in cached:
                return float(cached["lat"]), float(cached["lon"])
        self._sleep_rate()
        try:
            params = {
                "q": name,
                "format": "json",
                "limit": 1,
                "addressdetails": 0,
                "email": self.email,
            }
            headers = {"User-Agent": self.user_agent}
            r = requests.get(self.base_url, params=params, headers=headers, timeout=5)
            if r.status_code == 200:
                arr = r.json()
                if arr:
                    lat = float(arr[0]["lat"]); lon = float(arr[0]["lon"])
                    if self.cache:
                        self.cache.set_json(key, {"lat": lat, "lon": lon}, ttl=self.ttl)
                    return lat, lon
        except Exception:
            return None
        return None

class MapboxGeocoder(BaseGeocoder):
    def __init__(self, token: str, cache=None, ttl=86400):
        super().__init__(cache, ttl)
        self.token = token

    def geocode_city(self, name: str) -> Optional[Tuple[float, float]]:
        key = _hash_key("mapbox", name.lower())
        if self.cache:
            cached = self.cache.get_json(key)
            if cached:
                return float(cached["lat"]), float(cached["lon"])
        try:
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{requests.utils.quote(name)}.json"
            r = requests.get(url, params={"access_token": self.token, "limit": 1, "types": "place"}, timeout=5)
            if r.status_code == 200:
                j = r.json()
                feats = j.get("features", [])
                if feats:
                    lon, lat = feats[0]["center"]
                    if self.cache:
                        self.cache.set_json(key, {"lat": lat, "lon": lon}, ttl=self.ttl)
                    return float(lat), float(lon)
        except Exception:
            return None
        return None

class GoogleGeocoder(BaseGeocoder):
    def __init__(self, api_key: str, cache=None, ttl=86400):
        super().__init__(cache, ttl)
        self.api_key = api_key

    def geocode_city(self, name: str) -> Optional[Tuple[float, float]]:
        key = _hash_key("google", name.lower())
        if self.cache:
            cached = self.cache.get_json(key)
            if cached:
                return float(cached["lat"]), float(cached["lon"])
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            r = requests.get(url, params={"address": name, "key": self.api_key, "language": "en"}, timeout=5)
            if r.status_code == 200:
                j = r.json()
                if j.get("results"):
                    loc = j["results"][0]["geometry"]["location"]
                    lat, lon = loc["lat"], loc["lng"]
                    if self.cache:
                        self.cache.set_json(key, {"lat": lat, "lon": lon}, ttl=self.ttl)
                    return float(lat), float(lon)
        except Exception:
            return None
        return None

class ChainedGeocoder(BaseGeocoder):
    def __init__(self, geocoders: List[BaseGeocoder]):
        super().__init__(None, 0)
        self.geocoders = geocoders

    def geocode_city(self, name: str) -> Optional[Tuple[float, float]]:
        for g in self.geocoders:
            res = g.geocode_city(name)
            if res:
                return res
        return None
