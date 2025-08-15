
-- Watchers and hits
CREATE TABLE IF NOT EXISTS watchers (
  id UUID PRIMARY KEY,
  type TEXT NOT NULL,
  config JSONB NOT NULL DEFAULT '{}'::jsonb,
  interval_seconds INTEGER NOT NULL DEFAULT 3600,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  last_run_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS watcher_hits (
  id UUID PRIMARY KEY,
  watcher_id UUID NOT NULL REFERENCES watchers(id) ON DELETE CASCADE,
  fingerprint TEXT,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_watcher_hits_watcher_id ON watcher_hits (watcher_id);
CREATE INDEX IF NOT EXISTS idx_watcher_hits_fp ON watcher_hits (fingerprint);
