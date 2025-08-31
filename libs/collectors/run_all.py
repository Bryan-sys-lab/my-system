"""Run all collectors (opt-in aggregator).

This module discovers collector modules beneath `libs.collectors` and
invokes the first public callable in each module. It returns per-module
results and is intentionally conservative: failures from individual
collectors are captured and returned so callers can handle partial results.

Two primary entry points are provided:
- `run_all_collectors(...)` which returns a mapping of module -> result
- `run_all_stream(...)` which yields (module, result) tuples as collectors finish

Supports per-module overrides via `whitelist_meta` and optional subprocess
isolation (`use_processes`) to forcibly kill timed-out collectors.
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import pkgutil
import time
import concurrent.futures
import multiprocessing
import logging
from typing import Any, Dict, Iterator, List, Optional, Tuple

import libs.collectors as collectors_pkg

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger("collector_runner")


def log_event(event: str, **kwargs):
    """Emit a JSON log event."""
    record = {"event": event, **kwargs}
    try:
        logger.info(json.dumps(record, ensure_ascii=False))
    except Exception:
        logger.info(f"[log-failed] {event} {kwargs}")


def _candidate_functions(module) -> List[Tuple[str, Any]]:
    """Return list of (name, fn) for public callables in a module."""
    out: List[Tuple[str, Any]] = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(module, name)
        except Exception:
            continue
        if callable(obj) and inspect.isfunction(obj):
            out.append((name, obj))
    return out


def _call_with_fallbacks(fn, query: Optional[str], limit: int):
    """Call collector function trying common arg patterns (query+limit, query, none)."""
    tries = [(query, limit), (query,), ()]
    last_exc = None
    for args in tries:
        try:
            return fn(*args)
        except TypeError as e:
            last_exc = e
            continue
    raise last_exc


def _discover_modules(whitelist: Optional[List[str]] = None) -> List[str]:
    """Return list of collector module names (restricted if whitelist is given)."""
    if whitelist:
        return list(whitelist)
    mods: List[str] = []
    for _, name, _ in pkgutil.walk_packages(collectors_pkg.__path__, collectors_pkg.__name__ + '.'):
        mods.append(name)
    return mods


def run_all_collectors(
    query: Optional[str] = None,
    limit: int = 50,
    whitelist: Optional[List[str]] = None,
    *,
    timeout: Optional[float] = 30.0,
    max_workers: int = 8,
    collector_timeout: float = 10.0,
    retries: int = 1,
    backoff: float = 0.1,
    whitelist_meta: Optional[Dict[str, Dict[str, Any]]] = None,
    use_processes: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """Run all (or whitelisted) collectors concurrently and return results."""
    mods = _discover_modules(whitelist)
    work = [m for m in sorted(set(mods)) if not m.endswith('.run_all')]
    results: Dict[str, Dict[str, Any]] = {}

    def _run_module(mod_name: str) -> Tuple[str, Dict[str, Any]]:
        log_event("collector_start", module=mod_name)

        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            log_event("collector_import_failed", module=mod_name, error=str(e))
            return mod_name, {'ok': False, 'error': f'import failed: {e}'}

        candidates = _candidate_functions(mod)
        if not candidates:
            log_event("collector_no_callable", module=mod_name)
            return mod_name, {'ok': False, 'error': 'no public callable found'}

        prefer = [
            'fetch_channel', 'fetch_subreddit_json', 'search_recent', 'nitter_search',
            'fetch_rss', 'fetch_many', 'old_reddit_top', 'fetch_wayback_text',
            'latest_snapshot', 'user_media', 'page_posts', 'multi_subreddits',
            'fetch_url', 'run_search',
        ]
        fn = None
        for pname in prefer:
            for name, f in candidates:
                if name == pname:
                    fn = f
                    break
            if fn:
                break
        if not fn:
            fn = candidates[0][1]

        opts = (whitelist_meta or {}).get(mod_name, {}) if isinstance(whitelist_meta, dict) else {}
        mod_timeout = float(opts.get('collector_timeout', collector_timeout))
        mod_retries = int(opts.get('retries', retries))
        mod_backoff = float(opts.get('backoff', backoff))
        mod_use_processes = bool(opts.get('use_processes', use_processes))
        mod_memory_limit_mb = float(opts.get('memory_limit_mb', 0) or 0) or 0.0

        last_err = None
        for attempt in range(1, max(1, mod_retries) + 1):
            log_event("collector_attempt", module=mod_name, attempt=attempt)

            try:
                if mod_use_processes:
                    ctx = multiprocessing.get_context('spawn')

                    def _proc_target(conn):
                        try:
                            start = time.perf_counter()
                            res = _call_with_fallbacks(fn, query, limit)
                            duration = time.perf_counter() - start
                            conn.send(json.dumps({'ok': True, 'result': res, 'duration': duration}, default=str))
                        except Exception:
                            import traceback
                            try:
                                conn.send(json.dumps({'ok': False, 'error': traceback.format_exc()}))
                            except Exception:
                                try:
                                    conn.send(json.dumps({'ok': False, 'error': 'unserializable error'}))
                                except Exception:
                                    pass
                        finally:
                            try:
                                conn.close()
                            except Exception:
                                pass

                    parent_conn, child_conn = multiprocessing.Pipe()
                    p = ctx.Process(target=_proc_target, args=(child_conn,))
                    p.start()
                    child_conn.close()
                    start_wait = time.perf_counter()
                    while p.is_alive() and (time.perf_counter() - start_wait) < mod_timeout:
                        if mod_memory_limit_mb > 0:
                            try:
                                pid = p.pid
                                stat_path = f"/proc/{pid}/status"
                                if os.path.exists(stat_path):
                                    with open(stat_path, 'r') as sf:
                                        for line in sf:
                                            if line.startswith('VmRSS:'):
                                                parts = line.split()
                                                if len(parts) >= 2:
                                                    rss_kb = int(parts[1])
                                                    rss_mb = rss_kb / 1024.0
                                                    if rss_mb > mod_memory_limit_mb:
                                                        log_event("collector_memkill", module=mod_name, rss_mb=rss_mb)
                                                        try:
                                                            p.terminate()
                                                        except Exception:
                                                            pass
                                                        p.join(1)
                                                        last_err = MemoryError(f'collector exceeded memory limit {mod_memory_limit_mb}MB')
                                                        break
                            except Exception:
                                pass
                        time.sleep(0.05)
                    if p.is_alive():
                        log_event("collector_timeout", module=mod_name, timeout=mod_timeout)
                        try:
                            p.terminate()
                        except Exception:
                            pass
                        p.join(1)
                        if not last_err:
                            last_err = TimeoutError(f'collector timed out after {mod_timeout}s (attempt {attempt})')
                        continue
                    try:
                        if parent_conn.poll():
                            payload = parent_conn.recv()
                            try:
                                obj = json.loads(payload)
                            except Exception:
                                raise RuntimeError('invalid json from child')
                            if obj.get('ok'):
                                raw = obj.get('result')
                                attempt_duration = obj.get('duration')
                            else:
                                raise RuntimeError(obj.get('error', 'child error'))
                        else:
                            raise RuntimeError('no response from collector subprocess')
                    finally:
                        try:
                            parent_conn.close()
                        except Exception:
                            pass
                else:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as attempt_ex:
                        fut = attempt_ex.submit(_call_with_fallbacks, fn, query, limit)
                        try:
                            start = time.perf_counter()
                            raw = fut.result(timeout=mod_timeout)
                            attempt_duration = time.perf_counter() - start
                        except concurrent.futures.TimeoutError:
                            last_err = TimeoutError(f'collector timed out after {mod_timeout}s (attempt {attempt})')
                            log_event("collector_timeout", module=mod_name, timeout=mod_timeout)
                            continue

                if raw is None:
                    records: List[Any] = []
                elif isinstance(raw, (list, tuple)):
                    records = list(raw)
                else:
                    if hasattr(raw, '__iter__') and not isinstance(raw, (str, bytes, dict)):
                        records = list(raw)
                    else:
                        records = [raw]

                meta = {
                    'attempts': attempt,
                    'duration': float(attempt_duration) if 'attempt_duration' in locals() else None,
                    'used_process': mod_use_processes,
                }
                log_event("collector_success", module=mod_name, records=len(records), **meta)
                return mod_name, {'ok': True, 'records': records, 'meta': meta}
            except Exception as e:
                last_err = e
                log_event("collector_error", module=mod_name, attempt=attempt, error=str(e))
                if attempt < mod_retries:
                    time.sleep(mod_backoff * attempt)
                continue

        log_event("collector_failed", module=mod_name, error=str(last_err))
        return mod_name, {'ok': False, 'error': str(last_err)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_mod = {ex.submit(_run_module, m): m for m in work}
        try:
            for fut in concurrent.futures.as_completed(future_to_mod, timeout=timeout):
                mod_name, info = fut.result()
                results[mod_name] = info
        except concurrent.futures.TimeoutError:
            for fut, mod in future_to_mod.items():
                if fut.done():
                    try:
                        mod_name, info = fut.result()
                        results[mod_name] = info
                    except Exception as e:
                        results[mod] = {'ok': False, 'error': str(e)}
                else:
                    results[mod] = {'ok': False, 'error': 'timeout'}

    return results


def run_all_stream(
    query: Optional[str] = None,
    limit: int = 50,
    whitelist: Optional[List[str]] = None,
    *,
    timeout: Optional[float] = 30.0,
    max_workers: int = 8,
    collector_timeout: float = 10.0,
    retries: int = 1,
    backoff: float = 0.1,
    whitelist_meta: Optional[Dict[str, Dict[str, Any]]] = None,
    use_processes: bool = False,
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yield (module, info) tuples as collectors finish."""
    mods = _discover_modules(whitelist)
    work = [m for m in sorted(set(mods)) if not m.endswith('.run_all')]

    def _single(mod_name: str) -> Tuple[str, Dict[str, Any]]:
        res = run_all_collectors(
            query=query,
            limit=limit,
            whitelist=[mod_name],
            timeout=collector_timeout,
            max_workers=1,
            collector_timeout=collector_timeout,
            retries=retries,
            backoff=backoff,
            whitelist_meta=whitelist_meta,
            use_processes=use_processes,
        )
        if isinstance(res, dict):
            return mod_name, res.get(mod_name, {'ok': False, 'error': 'internal'})
        return mod_name, {'ok': False, 'error': 'internal'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_mod = {ex.submit(_single, m): m for m in work}
        try:
            for fut in concurrent.futures.as_completed(future_to_mod, timeout=timeout):
                try:
                    mod_name, info = fut.result()
                    yield mod_name, info
                except Exception as e:
                    mod = future_to_mod.get(fut)
                    yield mod, {'ok': False, 'error': str(e)}
        except concurrent.futures.TimeoutError:
            for fut, mod in future_to_mod.items():
                if fut.done():
                    try:
                        mod_name, info = fut.result()
                        yield mod_name, info
                    except Exception as e:
                        yield mod, {'ok': False, 'error': str(e)}
                else:
                    yield mod, {'ok': False, 'error': 'timeout'}


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--query', default='')
    p.add_argument('--limit', type=int, default=50)
    p.add_argument('--whitelist', nargs='*')
    args = p.parse_args()
    out = run_all_collectors(args.query or None, args.limit, whitelist=args.whitelist)
    print(json.dumps(out, indent=2, ensure_ascii=False))
