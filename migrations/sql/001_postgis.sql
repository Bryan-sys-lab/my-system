-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;
-- Optional if you plan to use H3 via postgis-h3 extension (not required for python h3)
-- CREATE EXTENSION IF NOT EXISTS h3; 

-- Table to store fused geo estimates
CREATE TABLE IF NOT EXISTS geo_estimates (
    id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,     -- e.g., 'post', 'image', 'profile'
    entity_id TEXT NOT NULL,       -- your foreign key/id
    ts TIMESTAMPTZ DEFAULT now(),
    method TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    radius_m DOUBLE PRECISION NOT NULL,
    signals JSONB NOT NULL,        -- array of signals with meta
    geom GEOGRAPHY(POINT, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lon, lat), 4326)) STORED,
    h3_9 TEXT                       -- optional; store computed H3 index string at resolution 9
);

CREATE INDEX IF NOT EXISTS idx_geo_estimates_geom ON geo_estimates USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_geo_estimates_h3_9 ON geo_estimates(h3_9);
CREATE INDEX IF NOT EXISTS idx_geo_estimates_entity ON geo_estimates(entity_type, entity_id);
