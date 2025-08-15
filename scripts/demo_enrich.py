import os, yaml
from PIL import Image
import io

from libs.geo.enrichment import GeoEnricher, build_geocoder_from_config, build_wifi_cell_resolvers
from libs.geo.providers.ip_geo import IPGeoProvider
from libs.geo.cache import RedisCache
from libs.geo.storage import save_estimate_postgis

def load_image(img_bytes, img_path):
    if img_bytes:
        return Image.open(io.BytesIO(img_bytes))
    if img_path:
        return Image.open(img_path)
    raise ValueError("no image data")

def main():
    cfg = yaml.safe_load(open("config/geo.yml"))
    cache = RedisCache(cfg["redis"]["url"]) if cfg.get("redis") else None

    geocoder_fn = build_geocoder_from_config(cfg.get("geocoders"), cache=cache)
    wifi_resolvers, cell_resolvers = build_wifi_cell_resolvers(cfg.get("wifi_cell"), cache=cache)

    ip_provider = None
    if cfg.get("ip_geo", {}).get("enabled") and cfg["ip_geo"].get("maxmind_mmdb_path"):
        ip_provider = IPGeoProvider(cfg["ip_geo"]["maxmind_mmdb_path"])

    enricher = GeoEnricher(
        ip_provider=ip_provider,
        geocoder=geocoder_fn,
        image_loader=load_image,
        wifi_resolvers=wifi_resolvers,
        cell_resolvers=cell_resolvers,
    )

    # Example record
    record = {
        "ip": "8.8.8.8",
        "text": "Met up in Nairobi today",
        "wifi": [{"bssid":"01:23:45:67:89:ab","rssi":-60}],
        # "cell": {"mcc": 639, "mnc": 02, "lac": 12345, "cid": 67890},
        # "image_path": "tests/photo_with_exif.jpg",
    }

    est = enricher.from_record(record)
    if est:
        print("Fused:", est.lat, est.lon, "±", est.radius_m, "m via", est.method)
        # Save to PostGIS with H3
        save_estimate_postgis(
            dsn=cfg["storage"]["postgis_dsn"],
            entity_type="example",
            entity_id="rec-123",
            estimate=est,
            h3_resolution=cfg["storage"].get("h3_resolution"),
        )
    else:
        print("No signals")

if __name__ == "__main__":
    main()
