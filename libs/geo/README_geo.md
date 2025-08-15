# Geo Enrichment & Triangulation (Full)

This extends the basic module with:

- **MaxMind GeoIP2** (local `.mmdb`)
- **Geocoders** (Nominatim/Mapbox/Google) behind a **Redis cache**
- **Wi‑Fi / Cell** positioning (Google Geolocation API, Mozilla Location Service) with caching
- **PostGIS** storage + optional **H3** index
- **Docker Compose** for PostGIS and Redis
- End‑to‑end wiring example: `scripts/demo_enrich.py`

## Quick start

1. `cp config/geo.example.yml config/geo.yml` and fill your keys/paths.
2. (Optional) Launch infra:
   ```bash
   docker compose -f docker/docker-compose.geo.yml up -d
   ```
3. Create tables:
   ```bash
   psql "$POSTGIS_DSN" -f migrations/sql/001_postgis.sql
   ```
4. Install deps in your app env:
   ```bash
   pip install geoip2 requests redis psycopg2-binary Pillow PyYAML h3
   ```
5. Run the demo:
   ```bash
   python scripts/demo_enrich.py
   ```

## Wiring into your collectors

After each item is collected, build a `record` dict including any signals you have (`ip`, `text`, `image_path` or `image_bytes`, `wifi`, `cell`, optional `lat`/`lon`), then:

```python
estimate = enricher.from_record(record)
if estimate:
    save_estimate_postgis(dsn, entity_type, entity_id, estimate, h3_resolution=9)
```

## Notes

- Respect provider ToS (e.g., Nominatim requires a valid contact email & rate limits).
- Cache aggressively via Redis to control costs and rate limits.
- All providers are **fail-safe**; if one is down, the enricher still fuses remaining signals.


## New: Media geotags, network hints, and visual landmarks

- **Images**: EXIF GPS + XMP sidecars → `exif_image` / `exif_sidecar` signals.
- **Videos**: `ffprobe` reads QuickTime `ISO6709` / `GPS*` tags → `exif_video` signals.
- **Network hints**: Extract `ip`, `wifi` (BSSID/SSID) from XMP/video tags and resolve via Wi‑Fi/Cell providers.
- **Landmarks**: CLIP + FAISS index lookup on sampled video frames and image files → `landmark_visual` signals.

### Dependencies
```
apt-get install ffmpeg
pip install pillow piexif exifread ffmpeg-python faiss-cpu torch torchvision clip-anytorch
```
(You can swap FAISS/CLIP packages to match your environment; the code fails safe if absent.)

### Config
```yaml
landmarks:
  enabled: true
  index_dir: "/data/landmarks_index"
  threshold: 0.25

video:
  frame_every_sec: 2
  frame_limit: 8
```
Place `index.faiss` and `meta.jsonl` in `index_dir`. Each `meta.jsonl` line must include at least `name`, `lat`, and `lon`.

### Use in code
```python
from libs.geo.enrichment import GeoEnricher, build_landmark_detector

lm = build_landmark_detector(cfg.get("landmarks"))
enricher = GeoEnricher(..., landmark_detector=lm,
                       video_frame_every_sec=cfg["video"]["frame_every_sec"],
                       video_frame_limit=cfg["video"]["frame_limit"])

record = {
  "image_path": "photo.jpg",
  "video_path": "clip.mov",
  "xmp_text": open("photo.xmp").read(),
  "text": "at the Eiffel Tower",
  "wifi": [{"bssid":"01:23:45:67:89:ab","rssi":-61}]
}
est = enricher.from_record(record)
```
