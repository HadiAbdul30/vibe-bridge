import json
from flask import Flask, request
import ollama

app = Flask(__name__)


class VibeBridge:

  def __init__(self):
    self.routes = {}

  def connect(self, trigger_event):
    def decorator(func):
      self.routes[trigger_event] = func
      return func

    return decorator


bridge = VibeBridge()


# ⚡ REAL LOCAL AI TRANSFORMER
def ai_transform(
    text,
    prompt=(
        "Rewrite this text into an exciting 1-sentence social media caption with"
        " emojis"
    ),
    model="llama3.2",
):
  """Uses local Ollama to dynamically rewrite content with ZERO API keys."""
  try:
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\nInput Text: {text}",
        }],
    )
    return response["message"]["content"].strip()
  except Exception as e:
    # Graceful fallback if Ollama isn't active
    return f"✨ [FALLBACK OPTIMIZED]: {text} (Ollama Error: {e})"


@app.route("/webhook/<source_event>", methods=["POST"])
def handle_webhook(source_event):
  payload = request.json or {}
  if source_event in bridge.routes:
    result = bridge.routes[source_event](payload)
    return json.dumps({"status": "handled", "result": result}), 200
  return json.dumps({"error": f"No pipeline for '{source_event}'"}), 404