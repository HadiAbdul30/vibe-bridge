# VibeBridge 🚀
### A Local-First AI Automation & Webhook Integration Framework

VibeBridge is a lightweight, Python-powered automation framework that connects webhooks, RSS feeds, and local AI into a unified workflow engine.

Built with **Flask, Ollama, and SQLite**, VibeBridge enables developers to create intelligent automation pipelines, transform content using locally running language models, and maintain a persistent audit trail—all while keeping AI processing on their own infrastructure.

Whether you're building content automation tools, connecting third-party platforms, or experimenting with AI-powered workflows, VibeBridge provides a simple and extensible foundation.

---

## ✨ Key Features

- **🤖 Local AI Processing** — Integrate locally hosted language models through Ollama without relying on external AI APIs.
- **🔗 Webhook-Driven Automation** — Trigger custom workflows through HTTP endpoints.
- **📡 RSS Feed Monitoring** — Monitor RSS feeds for new content using `feedparser`.
- **⚡ Intelligent Workflow Pipelines** — Connect incoming events to AI transformations and downstream actions.
- **📝 Persistent Audit Logging** — Record workflow executions in a local SQLite database.
- **🧵 Background Processing** — Run RSS polling and other background tasks using Python threading.
- **🛠️ Developer-Friendly API** — Define automation routes with a simple decorator-based interface.
- **💻 Companion CLI** — Trigger workflows and inspect execution logs directly from your terminal.
- **🔒 Local-First Architecture** — Keep AI inference and audit data on your machine, subject to the configuration of your integrations.

---

## 🏗️ Architecture

VibeBridge connects event sources, workflow handlers, local AI processing, and audit logging.

```text
             ┌─────────────────────────┐
             │      Event Sources      │
             │                         │
             │   Webhooks / RSS Feeds  │
             └────────────┬────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │     VibeBridge Engine   │
             │                         │
             │    Flask + Python       │
             └────────────┬────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │    Workflow Handlers    │
             │                         │
             │  Custom Python Logic    │
             └────────────┬────────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
    ┌────────────────────┐  ┌────────────────────┐
    │    Local AI Engine  │  │   External Actions │
    │                    │  │                    │
    │  Ollama + Llama 3.2 │  │  Platform Connectors│
    └────────────────────┘  └────────────────────┘
                │                   │
                └─────────┬─────────┘
                          ▼
             ┌─────────────────────────┐
             │      Audit Storage      │
             │                         │
             │   SQLite Database       │
             │   bridge_audit.db       │
             └─────────────────────────┘
```

### Workflow Overview

1. **Receive an event** through a webhook or an RSS monitoring process.
2. **Route the event** to the corresponding registered workflow handler.
3. **Process the data** using custom Python logic and, when needed, local AI inference.
4. **Execute actions** through configured integrations or custom application code.
5. **Record execution details** in the SQLite audit database.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core application logic |
| Web Framework | Flask | HTTP server and webhook routing |
| Local AI Runtime | Ollama | Local language model inference |
| AI Model | Llama 3.2 | Text transformation and generation |
| RSS Ingestion | feedparser | RSS feed parsing and monitoring |
| HTTP Requests | requests | HTTP communication with external services |
| Database | SQLite | Persistent execution and audit logs |
| Concurrency | Python threading | Background polling tasks |
| CLI | Python | Workflow triggering and log inspection |

---

## 📋 Prerequisites

Before installing VibeBridge, ensure you have the following:

- Python 3.10 or later
- Git
- Ollama installed and running
- The Llama 3.2 model downloaded locally

Verify your Python installation:

```bash
python --version
```

Install Ollama from the official website:

https://ollama.com/

Download the required model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running and the model is available before triggering AI-powered workflows.

---

## 📦 Installation

### 1. Clone the Repository

Replace the repository URL below with your actual GitHub repository URL.

```bash
git clone https://github.com/your-username/vibe-bridge.git
cd vibe-bridge
```

### 2. Create a Virtual Environment

Create an isolated Python environment:

```bash
python -m venv venv
```

Activate it.

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows — Command Prompt**

```cmd
venv\Scripts\activate.bat
```

**Windows — PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install flask requests feedparser ollama
```

To make dependency installation reproducible, you can also create a `requirements.txt` file containing:

```text
Flask
requests
feedparser
ollama
```

Install dependencies from that file:

```bash
pip install -r requirements.txt
```

### 4. Verify Ollama

Download the model:

```bash
ollama pull llama3.2
```

Check that the model is available:

```bash
ollama list
```

Ensure the Ollama service is accessible before proceeding.

---

## 🚀 Getting Started

### Step 1: Start the VibeBridge Engine

From the project directory, run:

```bash
python app.py
```

The Flask application should start and expose the local server at:

```text
http://localhost:5000
```

The application is expected to initialize its webhook routes and background RSS monitoring according to your implementation.

> **Note:** The exact startup behavior depends on how `app.py` and the bridge module initialize the application and background threads.

### Step 2: Define an Automation Workflow

VibeBridge uses a decorator-based interface to associate incoming events with Python functions.

For example, the following workflow accepts a YouTube video event and generates a social media caption using local AI.

```python
from bridge import ai_transform, app, bridge


@bridge.connect("youtube_new_video")
def handle_youtube_upload(data):
    """
    Process a new YouTube video event and generate a caption.
    """

    video_url = data.get("url", "")
    raw_title = data.get("title", "")

    # Generate a caption using the local AI engine.
    smart_caption = ai_transform(
        raw_title,
        prompt=(
            "Write a high-energy, one-sentence social media "
            "caption with relevant emojis."
        ),
        trigger_name="youtube_fanout",
    )

    # Add downstream actions here if needed.
    print(f"Fanout workflow completed for: {video_url}")

    return {
        "status": "success",
        "video_url": video_url,
        "caption": smart_caption,
    }
```

#### How It Works

1. `@bridge.connect("youtube_new_video")` registers the event handler.
2. The incoming payload provides the video URL and title.
3. `ai_transform()` sends the title for processing by the configured local AI model.
4. The generated caption is returned as part of the workflow response.

**Note:** The example assumes that `bridge.py` implements the `bridge.connect()` decorator and `ai_transform()` function. The actual implementation must also handle Ollama communication and workflow execution.

### Step 3: Trigger a Workflow

You can trigger a registered workflow through the companion CLI or an HTTP request.

#### Option A: Use the Companion CLI

```bash
python cli.py trigger youtube_new_video '{"url":"https://youtu.be/demo","title":"Building Local AI Frameworks"}'
```

This command assumes that `cli.py` supports the `trigger` subcommand and accepts a JSON payload.

#### Option B: Use cURL

Send a POST request to the corresponding webhook endpoint:

```bash
curl -X POST http://localhost:5000/webhook/youtube_new_video \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://youtu.be/demo",
       "title": "Building Local AI Frameworks"
     }'
```

The endpoint is expected to dispatch the payload to the registered handler and return its response.

A successful execution should return a JSON response similar to:

```json
{
  "status": "success",
  "video_url": "https://youtu.be/demo",
  "caption": "Building the future with local AI! 🚀"
}
```

The caption above is illustrative; actual output depends on the model's response.

---

## 📡 RSS Feed Monitoring

VibeBridge includes `feedparser` as its RSS ingestion component.

This enables workflows to monitor RSS feeds and react to newly published content.

Potential applications include:

- Automatically generating summaries of new articles.
- Creating social media captions for published content.
- Monitoring developer blogs and technology news.
- Triggering downstream workflows when new entries appear.
- Enriching incoming content with locally generated AI output.

### Example Workflow

A typical RSS automation pipeline could follow this pattern:

```text
RSS Feed
   |
   v
Feed Polling
   |
   v
Detect New Entry
   |
   v
Extract Title and URL
   |
   v
Generate AI Summary
   |
   v
Execute Configured Action
   |
   v
Write Audit Log
```

The exact configuration depends on the RSS polling implementation in your project.

---

## 📝 Audit Logging

VibeBridge uses SQLite for persistent workflow auditing.

The default database file is:

```text
bridge_audit.db
```

The audit database can be used to inspect workflow executions, troubleshoot errors, and review application activity.

### View Logs Using the CLI

```bash
python cli.py logs
```

This command assumes that the companion CLI implements a `logs` subcommand.

### Retrieve Logs Through the REST API

If your Flask application exposes the documented `/logs` endpoint, retrieve the logs using:

```bash
curl http://localhost:5000/logs
```

The endpoint is expected to return recent audit records in its configured response format.

### Why Audit Logging Matters

Persistent audit records help developers:

- Investigate failed workflow executions.
- Review automation activity.
- Troubleshoot integration issues.
- Track AI transformation requests.
- Build operational monitoring tools.

Avoid storing API keys, passwords, access tokens, or unnecessary sensitive payload data in audit logs.

---

## 🔌 Extensibility

VibeBridge is designed to support additional integrations and custom automation workflows.

Potential extensions include:

| Integration | Example Use Case |
|---|---|
| Discord | Publish generated content to channels |
| Telegram | Send automated messages and notifications |
| X | Prepare and publish social media content |
| YouTube | Process new video metadata |
| RSS | Monitor blogs, news, and content feeds |
| Custom Webhooks | Connect internal applications and services |

These integrations are extension ideas, not claims that all connectors are currently implemented.

Developers can build new connectors around the existing workflow interface and register handlers for the events they want to process.

---

## 🔐 Security Considerations

Before exposing VibeBridge beyond a trusted local development environment, review the following:

- **Webhook authentication:** Protect webhook endpoints against unauthorized requests.
- **Network exposure:** Bind the server to localhost during local development unless external access is required.
- **Request validation:** Validate incoming JSON payloads and reject malformed requests.
- **Rate limiting:** Restrict excessive requests to prevent resource exhaustion.
- **Error handling:** Return appropriate HTTP status codes without exposing internal exceptions.
- **Audit privacy:** Avoid logging credentials, tokens, or sensitive personal information.
- **Database access:** Protect the SQLite database and its backups from unauthorized access.
- **AI processing:** Review prompts and input data before passing content to local models.
- **Thread safety:** Ensure concurrent background tasks and webhook handlers safely access shared resources.

Local AI inference can reduce dependence on external AI services, but it does not automatically secure webhook traffic, external integrations, or application data.

For production deployments, use a suitable WSGI server, configure authentication and monitoring, and review the application's concurrency and persistence behavior.

---

## 🧪 Troubleshooting

### Ollama Is Not Responding

Verify that Ollama is installed and running:

```bash
ollama list
```

If necessary, start the Ollama service using the method appropriate for your operating system.

Confirm that the `llama3.2` model is available.

### Flask Dependencies Are Missing

Activate the virtual environment and reinstall the dependencies:

```bash
pip install -r requirements.txt
```

### The Webhook Returns an Error

Check that:

1. The Flask server is running.
2. The requested event name matches the registered handler.
3. The request contains valid JSON.
4. The webhook route is implemented correctly.
5. The application logs contain no relevant exceptions.

### Audit Logs Are Not Available

Verify that:

- The application has permission to write to its working directory.
- The database initialization code has executed.
- The `/logs` endpoint is registered.
- The CLI uses the correct database path.

---

## 🗺️ Roadmap

Potential future improvements include:

- [ ] Additional platform connectors.
- [ ] Configurable RSS polling intervals.
- [ ] Improved retry and failure-handling mechanisms.
- [ ] Workflow execution status tracking.
- [ ] Structured logging and improved observability.
- [ ] Webhook authentication and rate limiting.
- [ ] Environment-based configuration.
- [ ] Automated tests for workflow handlers.
- [ ] Docker-based deployment.
- [ ] A dashboard for inspecting workflow activity.
- [ ] Configurable AI models and transformation prompts.

This roadmap represents possible future development rather than a guarantee that these features are already available.

---

## 🤝 Contributing

Contributions are welcome!

VibeBridge is intended for developers interested in local-first AI, automation infrastructure, and extensible event-driven applications.

### How to Contribute

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Test the affected functionality.
5. Submit a pull request with a clear description of the changes.

For example:

```bash
git checkout -b feature/new-connector
```

After implementing and testing your changes, commit them and open a pull request.

### Contribution Ideas

- Develop integrations for additional platforms.
- Improve error handling and reliability.
- Add automated tests.
- Optimize RSS monitoring.
- Improve documentation.
- Strengthen security and request validation.

For substantial changes, consider opening an issue first to discuss the proposed implementation.

---

## 📄 License

VibeBridge is intended to be distributed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the complete license terms.

If the license file has not yet been added to the repository, create it before describing the project as officially licensed under MIT.

---

## 💡 Philosophy

VibeBridge is built around three principles:

- **Local-first AI:** Run language models on infrastructure you control.
- **Composable automation:** Connect events, Python handlers, and integrations into flexible workflows.
- **Transparent execution:** Maintain an audit trail to make automation easier to inspect and debug.

The goal is to make AI-powered automation accessible, extensible, and developer-friendly without requiring every workflow to depend on a hosted AI service.

---

**VibeBridge — Connect events. Run local AI. Automate your workflows.** 🚀