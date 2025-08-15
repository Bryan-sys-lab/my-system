from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import math
import time

@dataclass
class GeoSignal:
    source: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_m: Optional[float] = None  # 1-sigma uncertainty
    timestamp: float = field(default_factory=lambda: time.time())
    meta: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return self.lat is not None and self.lon is not None

@dataclass
class GeoEstimate:
    lat: float
    lon: float
    radius_m: float
    signals: List[GeoSignal] = field(default_factory=list)
    method: str = "weighted_fusion"

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def clamp_lat(lat: float) -> float:
    return max(-90.0, min(90.0, lat))

def wrap_lon(lon: float) -> float:
    # Normalize to [-180, 180)
    x = (lon + 180.0) % 360.0 - 180.0
    # Edge case when lon == 180
    if x == -180.0 and lon > 0:
        x = 180.0
    return x
