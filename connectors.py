import requests


def send_discord(webhook_url: str, content: str):
  """Sends a message or AI-transformed caption to a Discord channel."""
  payload = {"content": content}
  try:
    response = requests.post(webhook_url, json=payload, timeout=5)
    if response.status_code == 204:
      print("✅ Successfully posted to Discord!")
      return True
    else:
      print(f"❌ Discord error: {response.status_code} - {response.text}")
      return False
  except Exception as e:
    print(f"❌ Failed to reach Discord: {e}")
    return False


def send_telegram(token: str, chat_id: str, content: str):
  """Sends a message to a Telegram chat using a bot token."""
  url = f"https://api.telegram.org/bot{token}/sendMessage"
  payload = {"chat_id": chat_id, "text": content}
  try:
    response = requests.post(url, json=payload, timeout=5)
    if response.status_code == 200:
      print("✅ Successfully posted to Telegram!")
      return True
    else:
      print(f"❌ Telegram error: {response.text}")
      return False
  except Exception as e:
    print(f"❌ Failed to reach Telegram: {e}")
    return False