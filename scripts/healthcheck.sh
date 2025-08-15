#!/bin/bash
# 3. Health Checks & Alerts
set -e
API_URL="${API_URL:-http://localhost:8080/healthz}"
RETRIES=5
SLEEP=5
for i in $(seq 1 $RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")
  if [ "$STATUS" = "200" ]; then
    echo "Health check passed."
    exit 0
  fi
  echo "Health check failed ($STATUS), retrying in $SLEEP sec..."
  sleep $SLEEP
done
# Optional: send alert (Slack, email, WhatsApp, etc.)
echo "Service unhealthy after $RETRIES attempts!" >&2
python3 /app/scripts/alert.py "Health check failed for $API_URL after $RETRIES attempts!"
exit 1
