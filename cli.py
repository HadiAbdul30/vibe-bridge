import json
import sys
import requests

BASE_URL = "http://localhost:5000"


def show_usage():
  print("""
⚡ VibeBridge CLI Tool

Usage:
  python cli.py logs                      - View recent transaction logs
  python cli.py trigger <event> '<json>'  - Manually dispatch a bridge webhook

Examples:
  python cli.py logs
  python cli.py trigger youtube_new_video '{"url": "https://youtu.be/123", "title": "CLI Test"}'
""")


def view_logs():
  try:
    res = requests.get(f"{BASE_URL}/logs")
    if res.status_code == 200:
      data = res.json()
      print(f"\n📊 Total Audit Logs: {data.get('total_logs', 0)}\n")
      print("-" * 60)
      for log in data.get("logs", []):
        print(f"🆔 ID: {log['id']} | ⏰ {log['timestamp']}")
        print(f"⚡ Event: {log['trigger_event']}")
        print(f"📥 Input: {log['input_title']}")
        print(f"🤖 AI Output:\n{log['output_caption']}")
        print("-" * 60)
    else:
      print(f"❌ Error fetching logs: {res.status_code}")
  except Exception as e:
    print(f"⚠️ Could not connect to VibeBridge server at {BASE_URL}: {e}")


def send_trigger(event_name, json_str):
  try:
    payload = json.loads(json_str)
  except json.JSONDecodeError:
    print("❌ Invalid JSON format provided in arguments.")
    return

  try:
    res = requests.post(
        f"{BASE_URL}/webhook/{event_name}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )
    if res.status_code == 200:
      print(f"✅ Trigger Success [{res.status_code}]:")
      print(json.dumps(res.json(), indent=2))
    else:
      print(f"❌ Trigger Failed [{res.status_code}]: {res.text}")
  except Exception as e:
    print(f"⚠️ Could not connect to VibeBridge server at {BASE_URL}: {e}")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    show_usage()
    sys.exit(1)

  command = sys.argv[1].lower()

  if command == "logs":
    view_logs()
  elif command == "trigger" and len(sys.argv) >= 4:
    send_trigger(sys.argv[2], sys.argv[3])
  else:
    show_usage()