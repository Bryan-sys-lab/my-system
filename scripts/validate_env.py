#!/usr/bin/env python3
"""Validate presence of required environment variables in deploys/tests.

Exit with non-zero if required env vars are missing.
"""
import os
import sys

REQUIRED = [
    'DATABASE_URL',
    'REDIS_URL',
    'MINIO_ROOT_USER',
    'MINIO_ROOT_PASSWORD',
]

missing = [v for v in REQUIRED if not os.getenv(v)]
if missing:
    print('Missing required environment variables:')
    for m in missing:
        print(' -', m)
    sys.exit(1)

print('All required environment variables present.')
sys.exit(0)
