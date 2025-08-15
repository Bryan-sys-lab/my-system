# Integrated Geo Enrichment

This repository has been wired with the **geo enrichment + triangulation** add-on.

## One-shot runner (search/monitor -> enrich -> output)

```bash
python cli/bsearch.py --collect PACKAGE.MODULE:FUNC --query "your search" --limit 25 --jsonl-out results.jsonl
```

- The collectors entrypoint must yield dict records with keys like:
  - `id`, `entity_type`, `text`, `ip`, `image_path`/`image_bytes`, `video_path`, `wifi`, `cell`, `lat`, `lon`, `xmp_text`

- Location enrichment runs **alongside** your other enrichment. It will add:
  ```json
  "location": {
    "lat": 1.23, "lon": 4.56, "radius_m": 120, "method": "fused", "signals": [ ... ]
  }
  ```

## PostGIS + H3

- Use `docker/docker-compose.geo.yml` to start PostGIS and Redis for caching.
- Run migration:
  ```bash
  psql "$POSTGIS_DSN" -f migrations/sql/001_postgis.sql
  ```

## Config

Copy and edit:
```
cp config/geo.example.yml config/geo.yml
```
Fill:
- `ip_geo.maxmind_mmdb_path` -> GeoLite2-City.mmdb path
- API keys/tokens for geocoders and Wi-Fi/Cell resolvers
- `redis.url` and `storage.postgis_dsn`

## Wiring collectors

Your collectors function (referenced by `--collect`) should yield records. Example signature:
```python
def run_search(query: str, limit: int = 50):
    for item in fetch_items(query, limit):
        yield {
            "id": item.id,
            "entity_type": "post",
            "text": f"{item.title} {item.body}",
            "ip": item.ip,
            "image_path": item.image_path,
            "video_path": item.video_path,
            "wifi": item.wifi,   # list of {bssid, rssi}
            "cell": item.cell,   # {mcc, mnc, lac, cid}
            "lat": item.lat, "lon": item.lon,
        }
```
