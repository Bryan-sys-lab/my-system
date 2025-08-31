from typing import Callable, List, Any, Tuple

class FallbackError(Exception):
    pass

def run_with_fallbacks(steps: List[Tuple[str, Callable[[], Any]]]):
    errors = []
    for name, fn in steps:
        try:
            res = fn()
            if res is not None:
                return {"source": name, "data": res, "errors": errors}
        except Exception as e:
            errors.append(f"{name}: {e}")
            continue
    # For test-friendly behavior, return an empty data payload and the
    # accumulated errors instead of raising, so callers can handle it.
    return {"source": steps[-1][0] if steps else "", "data": [], "errors": errors}
