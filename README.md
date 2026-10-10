# ⚡ VibeBridge

> **The local-first, zero-cost, private AI automation framework.**  
> Bypass expensive cloud subscriptions and API keys. Route, transform, and broadcast your content workflows entirely on your own hardware.

---

## 🚀 Why VibeBridge?

Most automation platforms (like Zapier or Make) and heavy orchestration frameworks (like LangChain) force you into expensive cloud tiers, complex setups, or recurring API micro-charges. 

**VibeBridge** takes a different approach:
* **$0 / Free Forever:** Powered entirely by local hardware using [Ollama](https://ollama.com) (e.g., Llama 3.2). Run 10,000+ transformations for free.
* **100% Private:** Your content data never leaves your machine. No third-party cloud data harvesting.
* **Zero API Keys Required:** Leverage background thread polling and open RSS streams to track feeds without developer tokens.
* **Pythonic Ergonomics:** Express entire pipelines cleanly using intuitive decorators (`@bridge.connect`).
* **Built-in Auditability:** Every transaction is timestamped and persisted in SQLite, viewable instantly via a native REST endpoint or CLI.

---

## 🏗️ Architecture Overview

```text
[ YouTube RSS / Webhook ] 
         │
         ▼
  ( Flask Server ) ──► @bridge.connect("event_name")
                           │
                           ▼
                 [ Local AI (Ollama) ] 
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
   [ Platform Dispatch A ]       [ Platform Dispatch B ]
            │                             │
            └──────────────┬──────────────┘
                           ▼
               [ SQLite Audit Trail ] 💾