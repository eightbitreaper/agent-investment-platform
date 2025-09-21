# System Architecture

This document describes the high-level architecture of the **Agent Investment Platform**.  
It will evolve as the system is designed and implemented.

---

## Goals

- Provide actionable insights based on stock/ETF/bond trends, news, and sentiment analysis.
- Run privately and securely, without direct internet exposure of core services.
- Be modular, with agents/tools specialized for different data sources (YouTube, Reddit, APIs, etc.).
- Generate daily/hourly Markdown reports that can be versioned in GitHub.

---

## High-Level Overview

```
+------------------+
|  User / Operator |
+------------------+
        |
        v
+-------------------+        +------------------+
| Conversational UI | <----> | Markdown Reports |
+-------------------+        +------------------+
        |
        v
+-------------------------------------------------+
|          Agent Orchestration Layer              |
| (coordinates specialized tools and data agents) |
+-------------------------------------------------+
   |        |         |          |          |
   v        v         v          v          v
 YouTube   Reddit   Stock API   News API   Backtesting
 Agent     Agent     Agent       Agent     Engine
```

---

## Components

### 1. Agent Orchestration Layer
- Central controller coordinating specialized agents.
- Receives user goals/strategies and dispatches tasks.
- Aggregates results into structured Markdown reports.

### 2. Data Source Agents
- **YouTube Agent** — fetches transcripts from configured channels.  
- **Reddit Agent** — scrapes posts/comments from configurable subreddits.  
- **Stock API Agent** — retrieves price data, charts, and technical indicators.  
- **News Agent** — pulls relevant news articles (Google/Bing, etc.).  

### 3. Analysis Layer
- Sentiment analysis (LLM-assisted).
- Strategy mapping (value vs. meme stocks, configurable by user).
- Backtesting to compare predictions with actual outcomes.

### 4. Reporting Layer
- Outputs structured Markdown summaries.  
- Includes daily/hourly reports and retrospective corrections.  
- Pushes reports into GitHub for versioning and collaboration.

### 5. Interfaces
- **Conversational UI** — debugging, clarifications, real-time queries.  
- **Markdown Reports** — official record, shared via GitHub.  
- **(Optional)** Email or alert system for urgent events.

---

## Deployment

- **Primary environment:** Windows desktop (with NVIDIA GPU for LLM acceleration).  
- **Containerized services:** Run via Docker/WSL2.  
- **Hybrid LLM strategy:**  
  - Local models (for privacy and GPU use).  
  - Cloud-hosted LLMs (fallback for heavier workloads, via ChatGPT Plus or other APIs).

---

## Security Considerations

- No external exposure — services run locally or behind secure tunnels.  
- Sensitive data (API keys, credentials) managed via `.env` files.  
- GitHub repo for collaboration, but no secrets checked in.

---

## Open Questions

- Which stock APIs offer the best tradeoff between cost, latency, and completeness?  
- Should backtesting be implemented as a standalone service or within each agent?  
- Do we need database persistence (e.g., Postgres/SQLite) for incremental learning, or will flat-file Markdown + Git history be sufficient?  

