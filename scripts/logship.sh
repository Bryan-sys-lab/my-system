#!/bin/bash
# 5. Log Collection & Monitoring
# Ships logs to stdout and, if LOG_ENDPOINT is set, to a remote endpoint (Grafana Loki, Sentry, etc.)
LOG_FILE="/data/app.log"
LOG_ENDPOINT="${LOG_ENDPOINT:-}" # Set this env var to enable remote log shipping
tail -F "$LOG_FILE" | while read line; do
  echo "$line"
  if [ -n "$LOG_ENDPOINT" ]; then
    curl -X POST -H "Content-Type: text/plain" --data "$line" "$LOG_ENDPOINT" || true
  fi
done
