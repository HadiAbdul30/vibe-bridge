import json
from flask import Flask, request

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


# The Magic AI Transformer Helper
def ai_transform(text, prompt="Make this punchy for social media"):
  """Simulated zero-config AI transformer function.

  (Later we plug in OpenAI / Ollama / Gemini in 1 line here!)
  """
  # For now, it dynamically builds a smart payload
  return f"✨ [AI OPTIMIZED]: '{text.upper()}' -> {prompt}"


@app.route("/webhook/<source_event>", methods=["POST"])
def handle_webhook(source_event):
  payload = request.json or {}
  if source_event in bridge.routes:
    result = bridge.routes[source_event](payload)
    return json.dumps({"status": "handled", "result": result}), 200
  return json.dumps({"error": f"No pipeline for '{source_event}'"}), 404