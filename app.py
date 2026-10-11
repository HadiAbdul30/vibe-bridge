import json
import sqlite3
from flask import Flask, jsonify, render_template, request
import ollama
import requests

app = Flask(__name__)

DB_NAME = "bridge_audit.db"


# ------------------------------------------------------------------------------
# 1. Database Initialization (Diary & Settings)
# ------------------------------------------------------------------------------
def init_db():
    """Ensure SQLite audit logs and settings tables exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_name TEXT NOT NULL,
            payload TEXT NOT NULL,
            result TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def log_event(trigger_name: str, payload: dict, result: str):
    """Persist event executions into SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (trigger_name, payload, result) VALUES (?, ?, ?)",
        (trigger_name, json.dumps(payload), result),
    )
    conn.commit()
    conn.close()


def get_setting(key: str) -> str:
    """Retrieve credential settings from the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""


def save_setting(key: str, value: str):
    """Save or update credential settings in the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()
    conn.close()


init_db()


# ------------------------------------------------------------------------------
# 2. VibeBridge Core Engine & Connectors
# ------------------------------------------------------------------------------
class VibeBridge:

    def __init__(self):
        self.routes = {}

    def connect(self, trigger_name: str):
        """Decorator to register automation pipelines."""

        def decorator(func):
            self.routes[trigger_name] = func
            return func

        return decorator


bridge = VibeBridge()


def dispatch_to_connectors(content: str):
    """Broadcasts content to any configured platform dynamically."""
    results = {}

    # 1. Discord
    discord_url = get_setting("discord_webhook")
    if discord_url:
        try:
            res = requests.post(discord_url, json={"content": content}, timeout=5)
            results["discord"] = res.status_code == 204
        except Exception:
            results["discord"] = False

    # 2. Slack
    slack_url = get_setting("slack_webhook")
    if slack_url:
        try:
            res = requests.post(slack_url, json={"text": content}, timeout=5)
            results["slack"] = res.status_code == 200
        except Exception:
            results["slack"] = False

    # 3. Telegram
    tg_token = get_setting("telegram_token")
    tg_chat = get_setting("telegram_chat_id")
    if tg_token and tg_chat:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            res = requests.post(
                url, json={"chat_id": tg_chat, "text": content}, timeout=5
            )
            results["telegram"] = res.status_code == 200
        except Exception:
            results["telegram"] = False

    # 4. Microsoft Teams
    teams_url = get_setting("teams_webhook")
    if teams_url:
        try:
            res = requests.post(teams_url, json={"text": content}, timeout=5)
            results["teams"] = res.status_code == 200
        except Exception:
            results["teams"] = False

    # 5. Custom Webhook
    custom_url = get_setting("custom_webhook")
    if custom_url:
        try:
            res = requests.post(
                custom_url,
                json={"message": content, "source": "VibeBridge"},
                timeout=5,
            )
            results["custom"] = res.status_code in [200, 201, 204]
        except Exception:
            results["custom"] = False

    return results


# ------------------------------------------------------------------------------
# 3. Local AI Brain (Ollama)
# ------------------------------------------------------------------------------
def ai_transform(text_input: str, prompt: str) -> str:
    """Stable single-pass local AI execution."""
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text_input},
            ],
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Ollama Error (Is Ollama running?): {str(e)}"


# ------------------------------------------------------------------------------
# 4. Automation Pipelines (Code-First Triggers)
# ------------------------------------------------------------------------------
@bridge.connect("youtube_new_video")
def handle_youtube_upload(data):
    video_url = data.get("url", "")
    raw_title = data.get("title", "")

    smart_caption = ai_transform(
        raw_title,
        prompt=(
            "Write a concise, high-energy 1-sentence social media caption with"
            " emojis."
        ),
    )
    final_message = f"📢 **New Video Upload!**\n{smart_caption}\n🔗 {video_url}"

    dispatch_to_connectors(final_message)
    log_event("youtube_new_video", data, final_message)
    return {"status": "success", "broadcast": final_message}


@bridge.connect("github_new_pr")
def handle_github_pr(data):
    repo = data.get("repository", "vibe-bridge")
    pr_title = data.get("title", "New Pull Request")

    smart_summary = ai_transform(
        pr_title,
        prompt=(
            "Summarize this pull request title into a professional 1-sentence"
            " changelog update."
        ),
    )
    final_message = f"💻 **GitHub PR Update** (`{repo}`)\n{smart_summary}"

    dispatch_to_connectors(final_message)
    log_event("github_new_pr", data, final_message)
    return {"status": "success", "broadcast": final_message}


# ------------------------------------------------------------------------------
# 5. Webhook, Settings & API Routes
# ------------------------------------------------------------------------------
@app.route("/webhook/<trigger_name>", methods=["POST"])
def trigger_webhook(trigger_name):
    if trigger_name not in bridge.routes:
        return jsonify({"error": f"No handler registered for '{trigger_name}'"}), 404

    data = request.get_json(force=True, silent=True) or {}
    handler = bridge.routes[trigger_name]
    result = handler(data)
    return jsonify(result), 200


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.form
    for key, value in data.items():
        if value.strip():
            save_setting(key, value.strip())
        else:
            save_setting(key, "")
    return '<span class="text-emerald-400 font-medium">✅ Configurations saved successfully!</span>'


@app.route("/api/test/<platform>", methods=["POST"])
def test_platform(platform):
    key_map = {
        "discord": "discord_webhook",
        "slack": "slack_webhook",
        "teams": "teams_webhook",
        "custom": "custom_webhook",
    }
    if platform not in key_map:
        return '<span class="text-red-400 text-xs">Invalid platform</span>', 400

    url = get_setting(key_map[platform])
    if not url:
        return (
            f'<span class="text-amber-400 text-xs">⚠️ Configure {platform} URL first</span>',
            400,
        )

    test_message = (
        "🧪 **VibeBridge Test Ping:** Connection established successfully!"
    )
    try:
        if platform == "discord":
            res = requests.post(url, json={"content": test_message}, timeout=5)
            success = res.status_code == 204
        elif platform in ["slack", "teams"]:
            res = requests.post(url, json={"text": test_message}, timeout=5)
            success = res.status_code in [200, 201]
        else:
            res = requests.post(
                url,
                json={"message": test_message, "source": "VibeBridge"},
                timeout=5,
            )
            success = res.status_code in [200, 201, 204]

        if success:
            return f'<span class="text-emerald-400 text-xs font-medium">✅ {platform.capitalize()} test passed!</span>'
        else:
            return f'<span class="text-red-400 text-xs">❌ Error code: {res.status_code}</span>'
    except Exception:
        return '<span class="text-red-400 text-xs">❌ Connection failed</span>'


@app.route("/api/webhooks", methods=["GET"])
def list_webhooks():
    webhook_list = [
        {
            "trigger_name": name,
            "endpoint_url": f"http://localhost:5000/webhook/{name}",
        }
        for name in bridge.routes.keys()
    ]
    return jsonify({"active_webhooks": webhook_list}), 200


# ------------------------------------------------------------------------------
# 6. Web UI Dashboard Routes
# ------------------------------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/webhooks-list")
def dashboard_webhooks_list():
    triggers = list(bridge.routes.keys())
    if not triggers:
        return '<p class="text-slate-500 text-sm font-mono">No webhooks registered yet.</p>'

    html = '<div class="space-y-3">'
    for trigger in triggers:
        url = f"http://localhost:5000/webhook/{trigger}"
        html += f"""
        <div class="flex items-center justify-between bg-obsidian border border-borderSubtle px-4 py-3 rounded-lg">
            <span class="font-medium text-slate-200 text-sm">{trigger}</span>
            <code class="text-xs font-mono bg-surface text-indigo-400 px-3 py-1.5 rounded border border-borderSubtle">{url}</code>
        </div>
        """
    html += "</div>"
    return html


@app.route("/dashboard/table")
def dashboard_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, trigger_name, payload, result, timestamp FROM audit_logs ORDER BY id DESC LIMIT 15"
    )
    logs = cursor.fetchall()
    conn.close()

    html = """
    <table class="w-full text-left border-collapse">
        <thead>
            <tr class="border-b border-borderSubtle bg-obsidian/50 text-slate-400 text-xs uppercase tracking-wider font-mono">
                <th class="py-3.5 px-6 font-semibold">ID</th>
                <th class="py-3.5 px-6 font-semibold">Trigger Event</th>
                <th class="py-3.5 px-6 font-semibold">Input Payload</th>
                <th class="py-3.5 px-6 font-semibold">AI Output & Dispatched Message</th>
                <th class="py-3.5 px-6 font-semibold">Timestamp</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-borderSubtle text-sm">
    """
    for log in logs:
        log_id, trigger, payload, result, timestamp = log
        html += f"""
        <tr class="hover:bg-surfaceHover/50 transition-colors">
            <td class="py-4 px-6 font-mono text-xs text-slate-400">#{log_id}</td>
            <td class="py-4 px-6 font-medium text-indigo-400">{trigger}</td>
            <td class="py-4 px-6 font-mono text-xs text-slate-400 max-w-xs truncate" title="{payload}">{payload}</td>
            <td class="py-4 px-6 font-mono text-xs text-slate-200 max-w-sm truncate" title="{result}">{result}</td>
            <td class="py-4 px-6 text-xs text-slate-500 font-mono">{timestamp}</td>
        </tr>
        """
    if not logs:
        html += '<tr><td colspan="5" class="py-8 text-center text-slate-500 font-mono text-sm">No automation events logged yet. Trigger a webhook to populate telemetry!</td></tr>'
    html += "</tbody></table>"
    return html


if __name__ == "__main__":
    print("⚡ Starting VibeBridge Linear-Grade Engine...")
    print("📍 Dashboard available at: http://localhost:5000/dashboard")
    app.run(host="0.0.0.0", port=5000, debug=True)