#!/usr/bin/env python3
"""Quick import-only smoke check for CI and local use.

Exits with non-zero on failure and prints helpful traceback.
"""
import importlib, traceback, sys

modules = ["apps", "libs"]
failed = False
for m in modules:
    try:
        importlib.import_module(m)
        print("IMPORT_OK", m)
    except Exception:
        print("IMPORT_FAIL", m)
        traceback.print_exc()
        failed = True

if failed:
    print("\nTip: set PYTHONPATH=. when running locally so the project packages are importable.")
    sys.exit(2)

print("SMOKE_OK")
