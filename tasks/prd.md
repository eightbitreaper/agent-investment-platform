# Product Requirements Document (PRD)
**Project:** AI Investment Platform (MCP Server Infrastructure)
**Audience:** Junior Developers & Contributors
**Format:** Markdown (`.md`)

---

## 1. Introduction / Overview
We are building an **AI-powered Investment Platform** using Model Context Protocol (MCP) servers designed to provide actionable insights into stock, ETF, and bond markets.

The platform provides:
- **Real-time stock data** through specialized MCP servers (Alpha Vantage, financial APIs)
- **Portfolio analysis** and performance tracking capabilities
- **Financial report generation** with automated insights and recommendations
- **Market news analysis** for sentiment and impact assessment
- **MCP protocol integration** for AI agent communication and tool access
- **Modular server architecture** allowing easy addition of new financial data sources

The system provides **decision-support tools** for human operators and integrates with MCP-compatible AI clients like Claude Desktop.

---

## 2. Goals
- Provide **timely insights** (hourly/daily configurable) on selected securities.
- Map **sentiment & news analysis → actionable recommendations** (buy/sell/hold, with reasoning).
- Maintain **Markdown logs** for transparency, backtesting, and error correction.
- Support **configurable strategies** (e.g., value investing, meme stocks, momentum).
- Keep the system **secure & private** (not exposed directly to the internet).
- Support a **hybrid model** (local LLM or external APIs like ChatGPT Plus).

---

## 3. User Stories
- *As an investor, I want to configure which stocks/ETFs/bonds I care about so I only get insights relevant to my portfolio.*
- *As an operator, I want the system to notify me via Markdown or email if urgent market-moving events occur.*
- *As a developer, I want a modular agent-based system so I can plug in new MCP data sources easily.*
- *As a researcher, I want to review Markdown logs to understand how past decisions were made and learn from errors.*
- *As a strategist, I want different accounts/strategies (value-based, meme-based) so insights are tailored to goals.*

---

## 4. Functional Requirements
1. **Data Ingestion**
   - The system must fetch **stock/ETF/bond price data** from APIs.
   - The system must support **YouTube transcript ingestion** from configurable channels.
   - The system must fetch **news headlines** from configurable sources (Google News, Bing News, Reddit, Twitter/X, etc.).

2. **Analysis**
   - The system must evaluate **technical chart trends**.
   - The system must perform **sentiment analysis** on news and transcripts.
   - The system must **map sentiment into actionable insights**.

3. **Output**
   - The system must generate **Markdown reports** (hourly/daily/weekly).
   - Reports must include: summary of events, actionable recommendations, supporting evidence.
   - Reports must be **pushed to GitHub** for versioned history.

4. **Interaction**
   - Provide a **conversational interface** (via VS Code agent, Obsidian, etc.).
   - Allow users to query data sources and debugging context.

5. **Learning & Backtesting**
   - System must track **past predictions vs actual outcomes**.
   - Reports should include **retroactive corrections** where applicable.

6. **Security**
   - Must not expose the system to the public internet.
   - Must support **private deployments** via Docker (Unraid, Windows, etc.).

---

## 5. Non-Goals
- The system will **not** directly execute trades.
- The system will **not** provide financial advice disclaimers (operator assumes responsibility).
- The system will **not** require training custom LLMs (will use APIs or local inference models).

---

## 6. Design Considerations
- **Deployment**:
  - Must support Docker-based deployment on Unraid or Windows.
  - Local + cloud hybrid (ChatGPT Plus for now, with option to swap LLMs).

- **Agents & Tools**:
  - MCP-based agents (YouTube transcripts, Reddit, stock APIs).
  - Specialized tools for chart analysis, sentiment, strategy mapping.

- **Scalability**:
  - Near real-time processing where possible.
  - Configurable polling intervals (hourly/daily/weekly).

- **User Interface**:
  - Markdown outputs (versioned in GitHub).
  - Conversational debugging via Copilot/Obsidian.

---

## 7. Technical Considerations
- Primary runtime: **Docker** (Unraid or Windows host).
- Host hardware options:
  - Windows desktop with **NVIDIA RTX 3090** (suitable for local inference).
  - Unraid server with Intel CPU (no dedicated GPU, but good for orchestration & Docker).
- Option to run **cloud-hosted LLMs** (ChatGPT Plus) for NLP tasks.
- Use **Cloudflare Tunnel** + **swag** if remote access needed (still private).

---

## 8. Success Metrics
- Timeliness of reports (must be generated on schedule).
- Accuracy of sentiment mapping vs real market outcomes.
- Developer adoption (ease of adding new MCP agents).
- Contribution growth (GitHub pull requests, community involvement).

---

## 9. Open Questions
- Which stock/ETF APIs provide the best free/low-cost balance for data access?
- How should urgency notifications (e.g., meme stock spikes) be delivered? (Email, Discord, etc.)
- Should reports include **confidence scores** for predictions?
- How can we best balance **local inference vs API usage** for cost and performance?

---
