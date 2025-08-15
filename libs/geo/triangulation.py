from __future__ import annotations
from typing import List, Optional
from .types import GeoSignal, GeoEstimate, clamp_lat, wrap_lon

def fuse(signals: List[GeoSignal]) -> Optional[GeoEstimate]:
    """Fuse multiple GeoSignals into a single GeoEstimate using inverse-variance weighting.
    If no signal has uncertainty, assign soft defaults by source.
    """
    if not signals:
        return None

    # Soft default 1-sigma uncertainties by signal type (meters)
    defaults = {
        "gps": 10.0,
        "exif": 50.0,
        "wifi": 100.0,
        "cell": 500.0,
        "ip": 20000.0,
        "checkin": 100.0,
        "text": 5000.0,
        "manual": 50.0,
    }

    # Prepare weights
    wsum = 0.0
    lat_acc = 0.0
    lon_acc = 0.0
    used = []

    for s in signals:
        if not s.is_valid():
            continue
        sigma = s.radius_m if (s.radius_m and s.radius_m > 0) else defaults.get(s.source, 10000.0)
        w = 1.0 / (sigma ** 2)
        wsum += w
        lat_acc += w * s.lat
        lon_acc += w * s.lon
        used.append((s, sigma))

    if wsum == 0 or not used:
        return None

    lat = clamp_lat(lat_acc / wsum)
    lon = wrap_lon(lon_acc / wsum)

    # Combined uncertainty: 1/sqrt(sum w_i)
    import math
    sigma = 1.0 / math.sqrt(wsum)

    estimate = GeoEstimate(lat=lat, lon=lon, radius_m=sigma, signals=[u[0] for u in used], method="weighted_fusion")
    return estimate
