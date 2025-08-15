from __future__ import annotations
from typing import Optional, Dict, Any, List
import json, re, subprocess, tempfile, os, shutil
from ..types import GeoSignal

ISO6709_RE = re.compile(r"([+-]\d+\.\d+)([+-]\d+\.\d+)")

def ffprobe_json(path: str) -> Optional[dict]:
    try:
        out = subprocess.check_output([
            "ffprobe","-v","error","-show_format","-show_streams","-print_format","json", path
        ], stderr=subprocess.STDOUT)
        return json.loads(out.decode("utf-8", "ignore"))
    except Exception:
        return None

def extract_geotag_from_probe(meta: dict) -> Optional[GeoSignal]:
    if not meta:
        return None
    tags = {}
    for k in ("format",):
        t = meta.get(k, {}).get("tags") or {}
        tags.update({str(kk).lower(): str(vv) for kk,vv in t.items()})
    # iOS QuickTime ISO6709 atom
    loc = tags.get("com.apple.quicktime.location.iso6709")
    if loc:
        m = ISO6709_RE.search(loc)
        if m:
            lat = float(m.group(1)); lon = float(m.group(2))
            return GeoSignal(source="exif_video", lat=lat, lon=lon, radius_m=50.0, meta={"tag": "iso6709"})
    # GPSLatitude/GPSLongitude if available
    try:
        lat = float(tags.get("gpslatitude")) if "gpslatitude" in tags else None
        lon = float(tags.get("gpslongitude")) if "gpslongitude" in tags else None
        if lat is not None and lon is not None:
            return GeoSignal(source="exif_video", lat=lat, lon=lon, radius_m=50.0, meta={"tag": "gps"})
    except Exception:
        pass
    return None

def extract_network_hints(meta: dict) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not meta:
        return out
    tags = {}
    for k in ("format",):
        t = meta.get(k, {}).get("tags") or {}
        tags.update({str(kk).lower(): str(vv) for kk,vv in t.items()})
    # IP addresses
    ip = re.search(r"(\b\d{1,3}(?:\.\d{1,3}){3}\b)", json.dumps(tags))
    if ip:
        out["ip"] = ip.group(1)
    # SSID/BSSID hints (rare)
    bssid = re.search(r"([0-9a-f]{2}(?::[0-9a-f]{2}){5})", json.dumps(tags))
    if bssid:
        out.setdefault("wifi", [])
        out["wifi"].append({"bssid": bssid.group(1)})
    return out

def sample_video_frames(path: str, out_dir: str, every_sec: int = 2, limit: int = 10) -> List[str]:
    # Extract at 1 frame per `every_sec` seconds, up to `limit` frames
    try:
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        # Use -vf fps=1/every_sec
        cmd = [
            "ffmpeg","-hide_banner","-loglevel","error","-i", path,
            "-vf", f"fps=1/{every_sec}", "-frames:v", str(limit),
            os.path.join(out_dir, "frame_%03d.jpg")
        ]
        subprocess.check_call(cmd)
        # Collect generated files
        frames = [os.path.join(out_dir, f) for f in sorted(os.listdir(out_dir)) if f.lower().endswith(".jpg")]
        return frames[:limit]
    except Exception:
        return []
