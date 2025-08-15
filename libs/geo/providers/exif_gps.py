from __future__ import annotations
from typing import Optional, Tuple
from ..types import GeoSignal

def _dms_to_deg(dms, ref) -> Optional[float]:
    try:
        deg, minutes, seconds = dms
        val = float(deg) + float(minutes)/60.0 + float(seconds)/3600.0
        if ref in ['S', 'W']:
            val = -val
        return val
    except Exception:
        return None

def from_pillow_image(img) -> Optional[GeoSignal]:
    try:
        exif = img.getexif()
        if not exif:
            return None
        gps = exif.get(34853)  # GPSInfo tag
        if not gps:
            return None

        lat = None; lon = None
        lat_ref = gps.get(1); lat_dms = gps.get(2)
        lon_ref = gps.get(3); lon_dms = gps.get(4)
        if lat_ref and lat_dms and lon_ref and lon_dms:
            lat = _dms_to_deg(lat_dms, lat_ref)
            lon = _dms_to_deg(lon_dms, lon_ref)

        if lat is not None and lon is not None:
            # Consumer camera EXIF jitter ~10-50m
            return GeoSignal(source="exif", lat=lat, lon=lon, radius_m=50.0, meta={"exif": True})
    except Exception:
        return None
    return None
