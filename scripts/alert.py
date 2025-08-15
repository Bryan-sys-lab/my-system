# Alert script for healthcheck failures, backup issues, etc.
import os
import requests

def send_alert(message):
    webhook = os.getenv('ALERT_WEBHOOK_URL')
    whatsapp_to = os.getenv('WHATSAPP_ALERT_TO')
    # Slack webhook example
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if webhook:
        try:
            requests.post(webhook, json={"text": message}, timeout=10)
        except Exception as e:
            print(f"Webhook alert failed: {e}")
    if slack_webhook:
        try:
            requests.post(slack_webhook, json={"text": message}, timeout=10)
        except Exception as e:
            print(f"Slack alert failed: {e}")
    if whatsapp_to:
        # Example: Twilio WhatsApp
        from twilio.rest import Client
        sid = os.getenv('TWILIO_ACCOUNT_SID')
        token = os.getenv('TWILIO_AUTH_TOKEN')
        from_num = os.getenv('TWILIO_WHATSAPP_FROM')
        if sid and token and from_num:
            try:
                client = Client(sid, token)
                client.messages.create(
                    body=message,
                    from_=from_num,
                    to=whatsapp_to
                )
            except Exception as e:
                print(f"WhatsApp alert failed: {e}")

if __name__ == "__main__":
    import sys
    send_alert(" ".join(sys.argv[1:]))
