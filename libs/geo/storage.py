from __future__ import annotations
from typing import Optional, Dict, Any
import json
import psycopg2

try:
    import h3
except Exception:
    h3 = None

def save_estimate_postgis(dsn: str, entity_type: str, entity_id: str, estimate, h3_resolution: Optional[int] = None):
    """Persist GeoEstimate into PostGIS with optional H3 index."""
    h3_index = None
    if h3 and h3_resolution:
        try:
            h3_index = h3.geo_to_h3(estimate.lat, estimate.lon, h3_resolution)
        except Exception:
            h3_index = None

    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO geo_estimates (entity_type, entity_id, method, lat, lon, radius_m, signals, h3_9)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        entity_type,
                        entity_id,
                        estimate.method,
                        float(estimate.lat),
                        float(estimate.lon),
                        float(estimate.radius_m),
                        json.dumps([s.__dict__ for s in estimate.signals]),
                        h3_index,
                    ),
                )
    finally:
        conn.close()
