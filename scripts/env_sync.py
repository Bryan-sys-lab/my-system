# 6. Environment Sync
import os
from dotenv import dotenv_values

REQUIRED = set()
with open('.env.example') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key = line.split('=',1)[0].strip()
            if key:
                REQUIRED.add(key)

render_env = {k for k in os.environ}
missing = REQUIRED - render_env
if missing:
    print(f"Missing required env vars: {', '.join(missing)}")
    exit(1)
else:
    print("All required env vars are set.")
