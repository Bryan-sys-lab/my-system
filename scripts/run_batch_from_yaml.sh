
#!/usr/bin/env bash
set -euo pipefail

YAML_FILE=${1:-feeds/kenya_batch_all.yaml}
API=${API:-http://localhost:8080}

PROJECT_ID=$(yq -r '.project' "$YAML_FILE")
RSS=$(yq '.rss // []' -o=json "$YAML_FILE")
TW=$(yq '.twitter_handles // []' -o=json "$YAML_FILE")
FB=$(yq '.facebook_pages // []' -o=json "$YAML_FILE")
IG=$(yq '.instagram_ids // []' -o=json "$YAML_FILE")
TG=$(yq '.telegram_chats // []' -o=json "$YAML_FILE")
DC=$(yq '.discord_channels // []' -o=json "$YAML_FILE")
MA=$(yq '.mastodon_instances // []' -o=json "$YAML_FILE")
BS=$(yq '.bluesky_handles // []' -o=json "$YAML_FILE")
TT=$(yq '.tiktok_users // []' -o=json "$YAML_FILE")
RD=$(yq '.reddit_subreddits // []' -o=json "$YAML_FILE")
DW=$(yq '.deepweb // {}' -o=json "$YAML_FILE")
ON=$(yq '.onion // {}' -o=json "$YAML_FILE")

curl -sS -X POST "$API/batch/run" -H "Content-Type: application/json" -d "{
  \"project_id\": \"$PROJECT_ID\",
  \"rss\": $RSS,
  \"twitter_handles\": $TW,
  \"facebook_pages\": $FB,
  \"instagram_ids\": $IG,
  \"telegram_chats\": $TG,
  \"discord_channels\": $DC,
  \"mastodon_instances\": $MA,
  \"bluesky_handles\": $BS,
  \"tiktok_users\": $TT,
  \"reddit_subreddits\": $RD,
  \"deepweb\": $DW,
  \"onion\": $ON
}"
