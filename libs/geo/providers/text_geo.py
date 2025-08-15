from __future__ import annotations
import re
from typing import List, Optional
from ..types import GeoSignal

# Very light-weight lat,lon parser and 'in <City>' detector. Real systems should call a geocoder.
LATLON_RE = re.compile(r"\b(-?\d{1,2}\.\d+),\s*(-?\d{1,3}\.\d+)\b")
IN_CITY_RE = re.compile(r"\bin\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b" )

def parse_latlon(text: str) -> List[GeoSignal]:
    out = []
    for m in LATLON_RE.finditer(text or ""):
        lat = float(m.group(1)); lon = float(m.group(2))
        out.append(GeoSignal(source="text", lat=lat, lon=lon, radius_m=2000.0, meta={"pattern": "latlon"}))
    return out

def parse_in_city(text: str) -> List[GeoSignal]:
    # Emits a GeoSignal with no coordinates; caller should geocode city -> coords
    out = []
    for m in IN_CITY_RE.finditer(text or ""):
        out.append(GeoSignal(source="text", lat=None, lon=None, radius_m=None, meta={"city": m.group(1)}))
    return out
