import os, requests

def channel_messages(channel_id: str, limit: int = 50):
    token = os.getenv("DISCORD_BOT_TOKEN","")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN not set")
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}
    params = {"limit": min(limit, 100)}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()
