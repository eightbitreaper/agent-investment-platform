# Agent Investment Platform - System Architecture

This document describes the comprehensive architecture of the **Agent Investment Platform** - a production-ready AI-powered financial analysis system with MCP server integration.

## 🎯 Architecture Goals

- **AI-Powered Analysis** - Automated stock, ETF, and bond analysis using LLMs and machine learning
- **Real-Time Data Integration** - Multi-source data aggregation from financial APIs, news, and social media
- **Modular MCP Architecture** - Specialized Model Context Protocol servers for different data domains
- **Automated Reporting** - Comprehensive markdown reports with GitHub version control integration
- **Production-Ready Infrastructure** - Docker orchestration, health monitoring, and enterprise-grade reliability
- **Security-First Design** - No sensitive data in code, environment-based configuration, secure API handling

## 🏗️ High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   LLM Services  │  │  Strategy Engine │  │ Report Generator │  │
│  │ (OpenAI/Claude/ │  │  (Investment     │  │ (Automated MD   │  │
│  │  Local Models)  │  │   Strategies)    │  │  with GitHub)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   MCP Protocol Layer  │
                    │ (JSON-RPC 2.0 + Tools)│
                    └───────────┬───────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Server Infrastructure                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │Stock Data   │ │News Analysis│ │Report Gen   │ │Analysis     │ │
│  │Server       │ │Server       │ │Server       │ │Engine Server│ │
│  │             │ │             │ │             │ │             │ │
│  │• Real-time  │ │• Multi-source│ │• Templates  │ │• Technical  │ │
│  │  quotes     │ │  aggregation│ │• GitHub pub │ │  analysis   │ │
│  │• Historical │ │• Sentiment  │ │• Chart gen  │ │• Fundamental│ │
│  │  data       │ │  analysis   │ │• Batch proc │ │  analysis   │ │
│  │• Fundamentals│ │• Social     │ │• Validation │ │• Risk assess│ │
│  │• Batch proc │ │  monitoring │ │             │ │• Portfolio  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Sources Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │Financial    │ │News & Media │ │Social Media │ │Market Data  │ │
│  │APIs         │ │Sources      │ │Platforms    │ │Providers    │ │
│  │             │ │             │ │             │ │             │ │
│  │• Polygon    │ │• NewsAPI    │ │• Reddit     │ │• YouTube    │ │
│  │  Vantage    │ │• Financial  │ │• Twitter    │ │• Transcripts│ │
│  │• Polygon    │ │  News feeds │ │• Discussion │ │• Educational│ │
│  │• Yahoo      │ │• Market     │ │  forums     │ │  content    │ │
│  │  Finance    │ │  reports    │ │             │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 System Components

### 1. MCP Server Infrastructure (Production-Ready)

**Stock Data Server** (`src/mcp_servers/stock_data_server.py`)
- **Real-time quotes** via Polygon API
- **Historical price data** with configurable timeframes
- **Company fundamentals** including P/E ratios, debt metrics, ROE
- **Batch processing** for multiple stock analysis
- **Rate limiting** and error handling for API stability

**Analysis Engine Server** (`src/mcp_servers/analysis_engine_server.py`)
- **Technical Analysis**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Fundamental Analysis**: DCF valuation, financial strength scoring
- **Risk Assessment**: Volatility, VaR, Sharpe ratio, Beta calculations
- **Portfolio Optimization**: Modern portfolio theory implementation
- **SQLite persistence** for analysis history and caching

**Report Generator Server** (`src/mcp_servers/report_generator_server.py`)
- **Template Engine**: Jinja2-based report templates
- **Multi-format Output**: Markdown, HTML with chart integration
- **GitHub Publishing**: Automated commit and push to repositories
- **Batch Processing**: Multiple report generation with error handling
- **Chart Generation**: Financial charts and visualization support

**News Analysis Server** (`src/mcp-servers/news-analysis-server.js`)
- **Multi-source Aggregation**: NewsAPI, Reddit, financial news feeds
- **Sentiment Analysis**: Real-time sentiment scoring of financial news
- **Social Media Monitoring**: Reddit discussion tracking and analysis
- **Trend Detection**: Automated identification of trending financial topics
- **News Summarization**: AI-powered summary generation with key insights

### 2. MCP Server Management System

**Server Manager** (`src/mcp_servers/manager.py`)
- **Orchestration**: Start, stop, restart individual or all servers
- **Health Monitoring**: Continuous health checks with auto-restart
- **Configuration Management**: Dynamic configuration loading and validation
- **Process Monitoring**: Memory usage, CPU tracking, performance metrics
- **Logging**: Comprehensive structured logging with rotation

**Unified Runner** (`run_mcp_server.py`)
- **Individual Server Execution**: Run specific servers for development/testing
- **Batch Server Management**: Start all servers with single command
- **Development Support**: Hot reload, debug mode, testing integration
- **Cross-Platform Support**: Windows PowerShell and Unix shell compatibility

### 3. Configuration and Environment Management

**Configuration Ecosystem**
- **MCP Servers** (`config/mcp-servers.json`) - Server definitions, ports, environment variables
- **LLM Configuration** (`config/llm-config.yaml`) - OpenAI, Claude, local model settings
- **Data Sources** (`config/data-sources.yaml`) - API keys, endpoints, rate limits
- **Investment Strategies** (`config/strategies.yaml`) - Strategy definitions and parameters
- **Notifications** (`config/notification-config.yaml`) - Email, Discord, alert settings

**Environment Management**
- **Environment Template** (`.env.example`) - 50+ environment variables with examples
- **Security Standards**: No sensitive data in code, environment-based configuration
- **Cross-Platform Setup**: Automated environment detection and configuration

### 4. Development and Testing Infrastructure

**Testing Framework** (`test_mcp_servers.py`)
- **Comprehensive Server Testing**: All MCP servers with mock data
- **Health Check Validation**: System component verification
- **Integration Testing**: End-to-end workflow validation
- **Performance Testing**: Response time and resource usage analysis

**Health Monitoring** (`scripts/health-check.py`)
- **System Component Validation**: Python environment, dependencies, configuration
- **API Connectivity Testing**: External API availability and authentication
- **Database Health**: SQLite connectivity and table validation
- **File System Checks**: Permissions, disk space, directory structure

**VS Code Integration**
- **20 Automation Tasks**: Complete development workflow automation
- **85+ Workspace Settings**: Optimized development environment
- **Development Guidelines**: Mandatory standards enforcement
- **Memory Bank System**: AI persistence across development sessions  
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

