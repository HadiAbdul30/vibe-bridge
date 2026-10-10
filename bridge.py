import json
import sqlite3
import threading
import time
from flask import Flask, request
import feedparser
import ollama

app = Flask(__name__)

DB_NAME = "bridge_audit.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_event TEXT,
            input_title TEXT,
            output_caption TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()


def log_to_db(trigger_event, input_title, output_caption):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO logs (trigger_event, input_title, output_caption) VALUES"
      " (?, ?, ?)",
      (trigger_event, input_title, output_caption),
  )
  conn.commit()
  conn.close()


class VibeBridge:

  def __init__(self):
    self.routes = {}
    self.seen_items = set()

  def connect(self, trigger_event):
    def decorator(func):
      self.routes[trigger_event] = func
      return func

    return decorator

  def start_youtube_listener(
      self, channel_id, trigger_event, interval_seconds=10
  ):
    def poll():
      rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
      print(
          f"📡 [LISTENER ACTIVE] Watching YouTube RSS Feed: {channel_id} every"
          f" {interval_seconds}s"
      )

      while True:
        try:
          feed = feedparser.parse(rss_url)
          if feed.entries:
            latest = feed.entries[0]
            video_id = latest.id

            if video_id not in self.seen_items:
              if self.seen_items:
                print(
                    f"\n🔔 [NEW YOUTUBE DETECTED]: {latest.title} ({latest.link})"
                )
                payload = {"url": latest.link, "title": latest.title}
                if trigger_event in self.routes:
                  self.routes[trigger_event](payload)

              self.seen_items.add(video_id)
        except Exception as e:
          print(f"⚠️ RSS Fetch Error: {e}")

        time.sleep(interval_seconds)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()


bridge = VibeBridge()


def ai_transform(
    text,
    prompt=(
        "Rewrite this text into an exciting 1-sentence social media caption with"
        " emojis"
    ),
    model="llama3.2",
    trigger_name="unknown",
):
  try:
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\nInput Text: {text}",
        }],
    )
    result = response["message"]["content"].strip()
    log_to_db(trigger_name, text, result)
    return result
  except Exception as e:
    fallback = f"✨ [FALLBACK]: {text}"
    log_to_db(trigger_name, text, fallback)
    return fallback


@app.route("/webhook/<source_event>", methods=["POST"])
def handle_webhook(source_event):
  payload = request.json or {}
  if source_event in bridge.routes:
    result = bridge.routes[source_event](payload)
    return json.dumps({"status": "handled", "result": result}), 200
  return json.dumps({"error": f"No pipeline for '{source_event}'"}), 404


# ⚡ NEW: Audit Log Viewer Endpoint
@app.route("/logs", methods=["GET"])
def view_logs():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row  # Return rows as dictionaries
  cursor = conn.cursor()
  cursor.execute(
      "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20"
  )  # Latest 20 logs
  rows = cursor.fetchall()
  conn.close()

  logs = [dict(row) for row in rows]
  return json.dumps({"total_logs": len(logs), "logs": logs}, indent=4), 200