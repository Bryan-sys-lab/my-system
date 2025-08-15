#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib, sys, json

from libs.integration.location_pipeline import Pipeline, load_config

def load_collectors(entrypoint: str):
    # entrypoint like "app.collectors:search"
    if ":" not in entrypoint:
        raise SystemExit("Collectors entrypoint must be like 'package.module:function'")
    mod_name, fn_name = entrypoint.split(":",1)
    mod = __import__(mod_name, fromlist=[fn_name])
    fn = getattr(mod, fn_name)
    return fn

def main():
    p = argparse.ArgumentParser(prog="bsearch", description="Run search/monitor and enrich with location")
    p.add_argument("--geo-config", default="config/geo.yml")
    p.add_argument("--collect", required=True,
                   help="Collectors entrypoint (e.g., 'app.collectors:run_search' or 'app.watchers:run_monitor')")
    p.add_argument("--query", help="Search query (passed to collectors)")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--jsonl-out", default="-", help="Where to write enriched JSONL ('-' for stdout)")
    args = p.parse_args()

    cfg = load_config(args.geo_config)
    pipeline = Pipeline(cfg)

    collect_fn = load_collectors(args.collect)
    # We expect collect_fn(query, limit) -> iterable of dict records
    try:
        records = collect_fn(args.query, args.limit)
    except TypeError:
        # fallback: collect_fn(query) or collect_fn()
        try:
            records = collect_fn(args.query)
        except TypeError:
            records = collect_fn()

    out_stream = sys.stdout if args.jsonl_out == "-" else open(args.jsonl_out, "w", encoding="utf-8")
    try:
        for enriched in pipeline.run(records):
            out_stream.write(json.dumps(enriched, ensure_ascii=False) + "\n")
            out_stream.flush()
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()

if __name__ == "__main__":
    main()
