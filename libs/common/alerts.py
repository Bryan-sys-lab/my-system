from libs.common.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_ALERT_TO
def whatsapp(message: str):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM and WHATSAPP_ALERT_TO):
        raise RuntimeError("Twilio WhatsApp not configured")
    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        body=message,
        to=WHATSAPP_ALERT_TO
    )


import requests

def send_webhook(url: str, payload: dict, timeout: int = 10):
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception as e:
        return False

def send_whatsapp(body: str):
    # Uses TWILIO_* env vars if set; otherwise no-op
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whats = os.getenv("TWILIO_WHATSAPP_FROM")
    to_whats = os.getenv("ALERTS_WHATSAPP_TO")
    if not all([sid, token, from_whats, to_whats]):
        return False
    try:
        from twilio.rest import Client
        cli = Client(sid, token)
        msg = cli.messages.create(
            from_=from_whats,
            to=to_whats,
            body=body[:1600]
        )
        return True if msg.sid else False
    except Exception:
        return False
