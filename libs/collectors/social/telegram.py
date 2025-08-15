import os, requests

def channel_updates(chat_id: str, limit: int = 50):
    token = os.getenv("TELEGRAM_BOT_TOKEN","")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    # Use getUpdates only for direct bot updates; for channels, use Bot API via getChat + message links when the bot is an admin.
    # Here we provide a generic recent update fetch for the bot.
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    updates = r.json().get("result", [])
    # Filter by chat_id if provided
    if chat_id:
        updates = [u for u in updates if str(u.get('message',{}).get('chat',{}).get('id')) == str(chat_id)]
    return updates[-limit:]
