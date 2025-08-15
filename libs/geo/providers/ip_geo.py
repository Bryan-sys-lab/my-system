from __future__ import annotations
from typing import Optional, Dict, Any
from ..types import GeoSignal

class IPGeoProvider:
    """MaxMind GeoIP2 City provider (local mmdb file)."""
    def __init__(self, mmdb_path: Optional[str] = None):
        self.mmdb_path = mmdb_path
        self.reader = None
        if mmdb_path:
            self._init_reader()

    def _init_reader(self):
        try:
            import geoip2.database
            self.reader = geoip2.database.Reader(self.mmdb_path)
        except Exception:
            self.reader = None

    def lookup(self, ip: str) -> Optional[GeoSignal]:
        try:
            if not self.reader and self.mmdb_path:
                self._init_reader()
            if not self.reader:
                return None
            resp = self.reader.city(ip)
            loc = resp.location
            if loc and loc.latitude is not None and loc.longitude is not None:
                # MaxMind reports accuracy_radius in km; use that if present
                acc_km = getattr(loc, "accuracy_radius", None)
                radius_m = float(acc_km) * 1000 if acc_km else 20000.0
                return GeoSignal(
                    source="ip",
                    lat=float(loc.latitude),
                    lon=float(loc.longitude),
                    radius_m=radius_m,
                    meta={
                        "continent": getattr(resp.continent, "code", None),
                        "country": getattr(resp.country, "iso_code", None),
                        "city": getattr(resp.city, "name", None),
                        "accuracy_radius_km": acc_km,
                    },
                )
        except Exception:
            return None
        return None
