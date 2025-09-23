# Configuration Guide

Comprehensive guide for configuring and customizing the Agent Investment Platform to match your investment strategy, risk tolerance, and technical requirements.

## Table of Contents

- [Overview](#overview)
- [Environment Configuration](#environment-configuration)
- [LLM Configuration](#llm-configuration)
- [Investment Strategy Configuration](#investment-strategy-configuration)
- [Data Sources Configuration](#data-sources-configuration)
- [Risk Management Configuration](#risk-management-configuration)
- [Notification Configuration](#notification-configuration)
- [MCP Server Configuration](#mcp-server-configuration)
- [Performance Optimization](#performance-optimization)
- [Security Configuration](#security-configuration)
- [Development Configuration](#development-configuration)

## Overview

The platform uses YAML configuration files for easy customization without code changes. All configuration files are located in the `config/` directory:

```
config/
├── llm-config.yaml              # LLM provider and model settings
├── strategies.yaml              # Investment strategies and risk rules
├── data-sources.yaml            # API keys and data source settings
├── risk_management.yaml         # Risk management parameters
├── notification-config.yaml     # Alert and notification settings
├── mcp-servers.json            # MCP server configurations
└── alert-config.yaml          # Alert rules and thresholds
```

## Environment Configuration

### Basic Environment Setup

Create a `.env` file in the project root with your API keys and settings:

```bash
# Core API Keys (get free keys from respective providers)
POLYGON_API_KEY=your_polygon_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# LLM API Keys (optional - only if using API-based LLMs)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Local LLM Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300
HF_HOME=models/.huggingface_cache

# Database Configuration
DATABASE_URL=sqlite:///data/investment_platform.db

# GitHub Integration (optional)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=your-username/investment-reports

# Notification Services (optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password
SLACK_WEBHOOK_URL=your_slack_webhook_url

# System Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
DATA_DIRECTORY=data/
CACHE_DIRECTORY=data_cache/
```

### Platform-Specific Environment Variables

**Windows PowerShell**:
```powershell
# Set environment variables
$env:POLYGON_API_KEY = \"your_api_key\"
$env:LLM_PROVIDER = \"local\"

# Or use .env file (recommended)
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Item -Path \"env:$name\" -Value $value
}
```

**Linux/macOS**:
```bash
# Export environment variables
export POLYGON_API_KEY=\"your_api_key\"
export LLM_PROVIDER=\"local\"

# Or source .env file
set -a; source .env; set +a
```

## LLM Configuration

Configure Large Language Models in `config/llm-config.yaml`:

### Provider Selection

```yaml
# Set your default LLM provider
default:
  provider: \"huggingface\"  # Options: huggingface, ollama, openai, anthropic, lmstudio
  model: \"microsoft/Phi-3-mini-4k-instruct\"
  max_tokens: 4096
  temperature: 0.1
  timeout: 120
```

### Local LLM Configuration

#### Hugging Face Models (Free)
```yaml
providers:
  huggingface:
    cache_dir: \"${HF_HOME:-models/.huggingface_cache}\"
    models_dir: \"models\"
    models:
      - name: \"microsoft/Phi-3-mini-4k-instruct\"
        description: \"Phi-3 Mini - Small, efficient model for general financial analysis\"
        context_length: 4096
        size_gb: 2.4
        use_cases: [\"general\", \"classification\", \"summarization\"]
      - name: \"ProsusAI/finbert\"
        description: \"FinBERT - BERT model fine-tuned for financial sentiment analysis\"
        context_length: 512
        size_gb: 0.4
        use_cases: [\"sentiment\", \"classification\", \"news_analysis\"]
```

#### Ollama Configuration
```yaml
providers:
  ollama:
    host: \"${OLLAMA_HOST:-http://localhost:11434}\"
    models:
      - name: \"llama3.1:8b\"
        description: \"Llama 3.1 8B - Fast and efficient for general analysis\"
        context_length: 128000
        use_cases: [\"general\", \"analysis\", \"summarization\"]
      - name: \"llama3.1:70b\"
        description: \"Llama 3.1 70B - High quality for complex reasoning\"
        context_length: 128000
        use_cases: [\"complex_analysis\", \"strategy\", \"research\"]
```

#### LM Studio Configuration
```yaml
providers:
  lmstudio:
    host: \"http://localhost:1234\"
    api_key: \"lm-studio\"
    timeout: 120
    models:
      - name: \"Meta-Llama-3.1-8B-Instruct\"
        use_cases: [\"general\", \"analysis\"]
```

### API-based LLM Configuration

#### OpenAI Configuration
```yaml
providers:
  openai:
    api_key: \"${OPENAI_API_KEY}\"
    models:
      - name: \"gpt-4-turbo-preview\"
        description: \"GPT-4 Turbo - Latest and most capable model\"
        context_length: 128000
        max_tokens: 4096
        use_cases: [\"complex_analysis\", \"strategy\", \"research\", \"reports\"]
      - name: \"gpt-3.5-turbo\"
        description: \"GPT-3.5 Turbo - Fast and cost-effective\"
        context_length: 16384
        max_tokens: 4096
        use_cases: [\"general\", \"summarization\", \"classification\"]
```

#### Anthropic Configuration
```yaml
providers:
  anthropic:
    api_key: \"${ANTHROPIC_API_KEY}\"
    models:
      - name: \"claude-3-sonnet-20240229\"
        description: \"Claude 3 Sonnet - Balanced performance and capability\"
        context_length: 200000
        max_tokens: 4096
        use_cases: [\"analysis\", \"research\", \"reports\"]
```

### Task-Specific Model Assignments

Assign specific models to different analysis tasks:

```yaml
task_assignments:
  stock_analysis:
    primary: \"microsoft/Phi-3-mini-4k-instruct\"
    fallback: \"gpt-4-turbo-preview\"
    temperature: 0.1

  market_sentiment:
    primary: \"ProsusAI/finbert\"
    fallback: \"claude-3-sonnet-20240229\"
    temperature: 0.2

  investment_strategy:
    primary: \"llama3.1:8b\"
    fallback: \"gpt-4-turbo-preview\"
    temperature: 0.3

  report_generation:
    primary: \"gpt-4-turbo-preview\"
    fallback: \"claude-3-sonnet-20240229\"
    temperature: 0.2
```

## Investment Strategy Configuration

Customize investment strategies in `config/strategies.yaml`:

### Strategy Examples

#### Conservative Growth Strategy
```yaml
strategies:
  conservative_growth:
    name: \"Conservative Growth\"
    description: \"Low-risk strategy focusing on stable dividend-paying stocks\"
    risk_level: \"low\"
    target_return: 0.08  # 8% annual target
    max_volatility: 0.12  # Maximum 12% volatility

    allocation:
      large_cap_growth: 0.35
      dividend_stocks: 0.30
      bonds: 0.20
      cash: 0.10
      international: 0.05

    entry_criteria:
      technical:
        rsi_max: 70
        ma_trend: \"bullish\"
        volume_confirmation: true
      fundamental:
        pe_ratio_max: 25
        debt_to_equity_max: 0.5
        dividend_yield_min: 0.02
        revenue_growth_min: 0.05
      sentiment:
        min_score: -0.2

    exit_criteria:
      stop_loss: 0.08
      take_profit: 0.15
      rsi_overbought: 80

    position_sizing:
      base_size: 0.05  # 5% base position
      max_size: 0.08   # 8% maximum position
      volatility_adjustment: true
```

#### Aggressive Growth Strategy
```yaml
  aggressive_growth:
    name: \"Aggressive Growth\"
    description: \"High-risk, high-reward strategy focusing on growth stocks\"
    risk_level: \"high\"
    target_return: 0.20  # 20% annual target
    max_volatility: 0.25  # Maximum 25% volatility

    allocation:
      growth_stocks: 0.50
      small_cap_growth: 0.25
      tech_stocks: 0.15
      cash: 0.05
      crypto_exposure: 0.05

    entry_criteria:
      technical:
        rsi_range: [30, 70]
        macd_bullish: true
        breakout_confirmation: true
        volume_spike: 1.5
      fundamental:
        revenue_growth_min: 0.15
        pe_growth_ratio_max: 1.5
        market_cap_min: 1000000000

    position_sizing:
      base_size: 0.06  # 6% base position
      max_size: 0.10   # 10% maximum position
      momentum_adjustment: true
```

### Risk Management Configuration

```yaml
risk_management:
  max_portfolio_risk: 0.15  # Maximum 15% portfolio risk
  max_single_position: 0.08  # Maximum 8% in any single position
  max_sector_exposure: 0.25  # Maximum 25% exposure to any sector
  stop_loss_default: 0.08  # Default 8% stop loss
  take_profit_default: 0.15  # Default 15% take profit
  position_sizing_method: \"kelly_criterion\"  # or fixed_percentage, volatility_adjusted
  rebalance_frequency: \"weekly\"  # daily, weekly, monthly, quarterly
```

### Market Condition Adjustments

```yaml
market_conditions:
  bull_market:
    rsi_threshold: 30
    ma_crossover_weight: 1.2
    momentum_weight: 1.3
  bear_market:
    rsi_threshold: 20
    ma_crossover_weight: 0.8
    cash_allocation_min: 0.2
  sideways_market:
    range_trading_enabled: true
    breakout_confirmation_required: true
```

## Data Sources Configuration

Configure external data sources in `config/data-sources.yaml`:

### Financial Data Sources

```yaml
financial_data:
  alpha_vantage:
    api_key: \"${ALPHA_VANTAGE_API_KEY}\"
    base_url: \"https://www.alphavantage.co/query\"
    rate_limit: 5  # requests per minute (free tier)
    capabilities:
      - real_time_quotes
      - historical_data
      - technical_indicators
      - fundamental_data
    priority: 1

  polygon:
    api_key: \"${POLYGON_API_KEY}\"
    base_url: \"https://api.polygon.io\"
    rate_limit: 1000  # requests per minute (paid tier)
    capabilities:
      - real_time_quotes
      - historical_data
      - options_data
    priority: 2
```

### News and Social Media Sources

```yaml
news_sources:
  news_api:
    api_key: \"${NEWS_API_KEY}\"
    base_url: \"https://newsapi.org/v2\"
    rate_limit: 1000  # requests per day (free tier)
    sources:
      - reuters
      - bloomberg
      - cnbc
      - wall-street-journal

  reddit:
    client_id: \"${REDDIT_CLIENT_ID}\"
    client_secret: \"${REDDIT_CLIENT_SECRET}\"
    subreddits:
      - investing
      - stocks
      - SecurityAnalysis
      - ValueInvesting
```

### Data Refresh Configuration

```yaml
data_management:
  refresh_intervals:
    stock_prices: 60        # seconds
    news_articles: 15       # minutes
    fundamental_data: 24    # hours

  cache_settings:
    enabled: true
    ttl_seconds: 3600
    max_size_mb: 1000
    compression: true

  data_quality:
    validation_enabled: true
    anomaly_detection: true
    missing_data_threshold: 0.05
```

## Risk Management Configuration

Detailed risk management settings in `config/risk_management.yaml`:

### Position Sizing Rules

```yaml
position_sizing:
  method: \"kelly_criterion\"  # kelly_criterion, fixed_percentage, volatility_adjusted

  kelly_criterion:
    confidence_level: 0.95
    max_kelly_fraction: 0.25  # Never risk more than 25% of Kelly
    min_position_size: 0.01   # Minimum 1% position
    max_position_size: 0.10   # Maximum 10% position

  fixed_percentage:
    base_position_size: 0.05  # 5% base position size

  volatility_adjusted:
    target_volatility: 0.15   # 15% target volatility
    lookback_period: 252      # days for volatility calculation
```

### Stop Loss Configuration

```yaml
stop_loss:
  method: \"trailing\"  # fixed, trailing, volatility_based

  trailing_stop:
    initial_stop: 0.08        # 8% initial stop loss
    trail_amount: 0.03        # 3% trailing amount
    max_stop: 0.15            # Maximum 15% stop loss

  volatility_based:
    atr_multiplier: 2.0       # 2x Average True Range
    min_stop: 0.05            # Minimum 5% stop
    max_stop: 0.20            # Maximum 20% stop
```

### Portfolio Risk Limits

```yaml
portfolio_limits:
  max_portfolio_risk: 0.15    # 15% maximum portfolio risk
  max_single_position: 0.08   # 8% maximum single position
  max_sector_exposure: 0.25   # 25% maximum sector exposure
  max_correlation: 0.70       # 70% maximum position correlation

  diversification:
    min_positions: 8          # Minimum number of positions
    max_positions: 20         # Maximum number of positions
    sector_diversification: true
    geographic_diversification: true
```

## Notification Configuration

Configure alerts and notifications in `config/notification-config.yaml`:

### Email Notifications

```yaml
notifications:
  email:
    enabled: true
    smtp_server: \"${EMAIL_SMTP_SERVER}\"
    smtp_port: 587
    smtp_user: \"${EMAIL_SMTP_USER}\"
    smtp_password: \"${EMAIL_SMTP_PASSWORD}\"
    from_address: \"${EMAIL_SMTP_USER}\"
    to_addresses:
      - \"your_email@example.com\"

    templates:
      daily_report: \"templates/email/daily_report.html\"
      alert: \"templates/email/alert.html\"
      error: \"templates/email/error.html\"
```

### Discord Integration

```yaml
  discord:
    enabled: true
    webhook_url: \"${DISCORD_WEBHOOK_URL}\"
    username: \"Investment Bot\"
    avatar_url: \"https://example.com/bot_avatar.png\"

    channels:
      alerts: \"${DISCORD_ALERTS_WEBHOOK}\"
      reports: \"${DISCORD_REPORTS_WEBHOOK}\"
      errors: \"${DISCORD_ERRORS_WEBHOOK}\"
```

### Slack Integration

```yaml
  slack:
    enabled: false
    webhook_url: \"${SLACK_WEBHOOK_URL}\"
    channel: \"#investments\"
    username: \"Investment Bot\"

    message_formatting:
      use_blocks: true
      include_charts: false
```

### Alert Rules

```yaml
alert_rules:
  portfolio_alerts:
    daily_loss_threshold: 0.05      # Alert if portfolio down 5% in a day
    weekly_loss_threshold: 0.10     # Alert if portfolio down 10% in a week
    position_loss_threshold: 0.12   # Alert if any position down 12%

  market_alerts:
    volatility_spike: 2.0           # Alert if VIX spikes 2x normal
    volume_spike: 1.5               # Alert if volume 1.5x average

  system_alerts:
    api_failures: 3                 # Alert after 3 consecutive API failures
    data_staleness_hours: 2         # Alert if data older than 2 hours
    server_downtime_minutes: 5      # Alert if server down for 5 minutes
```

## MCP Server Configuration

Configure MCP servers in `config/mcp-servers.json`:

```json
{
  \"servers\": {
    \"stock-data-server\": {
      \"command\": \"python\",
      \"args\": [\"src/mcp_servers/stock_data_server.py\"],
      \"env\": {
        \"POLYGON_API_KEY\": \"${POLYGON_API_KEY}\",
        \"ALPHA_VANTAGE_API_KEY\": \"${ALPHA_VANTAGE_API_KEY}\"
      },
      \"capabilities\": [
        \"stock_quotes\",
        \"historical_data\",
        \"technical_indicators\"
      ]
    },

    \"news-analysis-server\": {
      \"command\": \"node\",
      \"args\": [\"src/mcp-servers/news-analysis-server.js\"],
      \"env\": {
        \"NEWS_API_KEY\": \"${NEWS_API_KEY}\",
        \"REDDIT_CLIENT_ID\": \"${REDDIT_CLIENT_ID}\"
      },
      \"capabilities\": [
        \"news_sentiment\",
        \"social_sentiment\",
        \"trend_analysis\"
      ]
    },

    \"analysis-engine-server\": {
      \"command\": \"python\",
      \"args\": [\"src/mcp_servers/analysis_engine_server.py\"],
      \"env\": {
        \"LLM_PROVIDER\": \"${LLM_PROVIDER:-local}\"
      },
      \"capabilities\": [
        \"fundamental_analysis\",
        \"technical_analysis\",
        \"recommendation_engine\"
      ]
    }
  },

  \"client_config\": {
    \"timeout\": 30,
    \"retry_attempts\": 3,
    \"retry_delay\": 5
  }
}
```

## Performance Optimization

### Caching Configuration

```yaml
# Add to relevant config files
caching:
  enabled: true

  redis:
    host: \"localhost\"
    port: 6379
    db: 0
    password: \"${REDIS_PASSWORD}\"

  memory_cache:
    max_size_mb: 512
    ttl_seconds: 3600

  file_cache:
    directory: \"data_cache/\"
    max_size_gb: 5
    cleanup_interval_hours: 24
```

### Database Optimization

```yaml
database:
  connection_string: \"${DATABASE_URL}\"

  connection_pool:
    min_connections: 5
    max_connections: 20
    connection_timeout: 30

  query_optimization:
    enable_query_cache: true
    slow_query_threshold_ms: 1000
    log_slow_queries: true
```

### Parallel Processing

```yaml
processing:
  max_workers: 8
  batch_size: 100

  analysis_pipeline:
    parallel_stocks: 5
    parallel_indicators: 3

  data_collection:
    concurrent_requests: 10
    request_timeout: 30
```

## Security Configuration

### API Security

```yaml
security:
  api_keys:
    rotation_days: 90
    encryption_enabled: true

  rate_limiting:
    requests_per_minute: 60
    burst_limit: 10

  authentication:
    session_timeout_minutes: 60
    max_failed_attempts: 5
    lockout_duration_minutes: 15
```

### Data Protection

```yaml
data_protection:
  encryption:
    at_rest: true
    in_transit: true
    algorithm: \"AES-256\"

  backup:
    enabled: true
    frequency: \"daily\"
    retention_days: 30
    encryption: true

  audit_logging:
    enabled: true
    log_file: \"logs/audit.log\"
    include_sensitive_data: false
```

## Development Configuration

### Debug Settings

```yaml
# Development-specific settings
development:
  debug_mode: true
  verbose_logging: true

  mock_data:
    enabled: false
    directory: \"test_data/\"

  testing:
    use_test_database: true
    fast_mode: true
    skip_external_apis: false
```

### Logging Configuration

```yaml
logging:
  level: \"INFO\"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

  handlers:
    console:
      enabled: true
      level: \"INFO\"
      format: \"%(asctime)s - %(name)s - %(levelname)s - %(message)s\"

    file:
      enabled: true
      filename: \"logs/platform.log\"
      max_size_mb: 100
      backup_count: 5

    email:
      enabled: false
      level: \"ERROR\"
      smtp_server: \"${EMAIL_SMTP_SERVER}\"
```

## Configuration Validation

### Validation Commands

```powershell
# Validate all configuration files
python scripts/setup/validate-setup.py --config-only

# Validate specific configuration files
python -c \"
import yaml
with open('config/llm-config.yaml') as f:
    config = yaml.safe_load(f)
    print('LLM config is valid')
\"

# Test configuration with dry run
python orchestrator.py --test-mode --dry-run
```

### Common Configuration Issues

1. **Missing Environment Variables**:
   ```bash
   # Check for missing variables
   python -c \"
   import os
   required = ['POLYGON_API_KEY', 'NEWS_API_KEY']
   missing = [var for var in required if not os.getenv(var)]
   if missing: print(f'Missing: {missing}')
   else: print('All environment variables set')
   \"
   ```

2. **Invalid YAML Syntax**:
   ```bash
   # Validate YAML files
   python -c \"
   import yaml
   import glob
   for file in glob.glob('config/*.yaml'):
       try:
           with open(file) as f:
               yaml.safe_load(f)
           print(f'{file}: OK')
       except Exception as e:
           print(f'{file}: ERROR - {e}')
   \"
   ```

3. **API Key Testing**:
   ```powershell
   # Test API connectivity
   python scripts/setup/validate-setup.py --test-apis
   ```

## Related Documentation

- [Installation Guide](installation-guide.md) - Complete setup instructions
- [Local LLM Setup Guide](local-llm-setup.md) - Configure local language models
- [Docker Deployment Guide](../deployment/docker-deployment.md) - Production deployment
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common configuration issues
- [API Documentation](../api/README.md) - Technical API reference

## Next Steps

1. **Customize Your Configuration**: Edit the configuration files to match your investment strategy and risk tolerance
2. **Test Your Setup**: Run validation scripts to ensure everything is configured correctly
3. **Generate Your First Report**: Use the configured system to generate an investment analysis
4. **Monitor and Adjust**: Use the monitoring dashboard to track performance and adjust settings as needed

---

The configuration system is designed to be flexible and powerful while remaining easy to use. Start with the default configurations and gradually customize them as you become more familiar with the platform.
