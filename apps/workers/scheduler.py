
import time, os
from apps.workers.watchers import run_due_watchers

INTERVAL = int(os.getenv("WATCHER_TICK_SECONDS","60"))

if __name__ == "__main__":
    while True:
        try:
            res = run_due_watchers()
        except Exception:
            pass
        time.sleep(INTERVAL)
