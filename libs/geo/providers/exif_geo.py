from __future__ import annotations
from typing import Optional, Tuple, Dict, Any, List
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
        gps = exif.get(34853)  # GPSInfo
        if not gps:
            return None

        lat = None; lon = None
        lat_ref = gps.get(1); lat_dms = gps.get(2)
        lon_ref = gps.get(3); lon_dms = gps.get(4)
        if lat_ref and lat_dms and lon_ref and lon_dms:
            lat = _dms_to_deg(lat_dms, lat_ref)
            lon = _dms_to_deg(lon_dms, lon_ref)

        if lat is not None and lon is not None:
            return GeoSignal(source="exif_image", lat=lat, lon=lon, radius_m=50.0, meta={"exif": True})
    except Exception:
        return None
    return None

def from_piexif_bytes(jpeg_bytes: bytes) -> Optional[GeoSignal]:
    try:
        import piexif, io, PIL.Image
        img = PIL.Image.open(io.BytesIO(jpeg_bytes))
        return from_pillow_image(img)
    except Exception:
        return None

def parse_sidecar_xmp(xmp_text: str) -> Optional[GeoSignal]:
    # Basic parse of ISO6709 location or GPS tags in XMP
    try:
        # ISO6709 example: +12.3456+078.9012+012.3/
        m = re.search(r"([+-]\d+\.\d+)([+-]\d+\.\d+)", xmp_text)
        if m:
            lat = float(m.group(1)); lon = float(m.group(2))
            return GeoSignal(source="exif_sidecar", lat=lat, lon=lon, radius_m=50.0, meta={"format": "iso6709"})
        # GPSLatitude/GPSLongitude if present
        lat_m = re.search(r"<exif:GPSLatitude>([-\d\.]+)</exif:GPSLatitude>", xmp_text)
        lon_m = re.search(r"<exif:GPSLongitude>([-\d\.]+)</exif:GPSLongitude>", xmp_text)
        if lat_m and lon_m:
            return GeoSignal(source="exif_sidecar", lat=float(lat_m.group(1)), lon=float(lon_m.group(1)), radius_m=50.0, meta={"format": "xmp"})
    except Exception:
        return None
    return None

def extract_network_from_xmp(xmp_text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        # Some camera apps embed SSID/BSSID
        ssid = re.search(r"<xmp:WiFiSSID>([^<]+)</xmp:WiFiSSID>", xmp_text)
        bssid = re.search(r"<xmp:WiFiBSSID>([^<]+)</xmp:WiFiBSSID>", xmp_text)
        if ssid or bssid:
            out.setdefault("wifi", [])
            out["wifi"].append({"ssid": ssid.group(1) if ssid else None, "bssid": bssid.group(1) if bssid else None})
        # IP hint
        ip = re.search(r"(\b\d{1,3}(?:\.\d{1,3}){3}\b)", xmp_text)
        if ip:
            out["ip"] = ip.group(1)
    except Exception:
        pass
    return out
