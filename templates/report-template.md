# {{title}}

## Executive Summary

**Analysis Date:** {{data.analysis_date}}
**Report Type:** {{data.report_type}}
**Period:** {{data.period}}
**Overall Recommendation:** {{data.recommendation | upper}}

{% if data.key_highlights %}
### Key Highlights
{% for highlight in data.key_highlights %}
- {{highlight}}
{% endfor %}
{% endif %}

## Market Overview

{% if data.market_overview %}
**Market Status:** {{data.market_overview.status}}
**Market Sentiment:** {{data.market_overview.sentiment}}

### Major Indices Performance
| Index | Value | Change | Change % |
|-------|-------|--------|----------|
{% for index in data.market_overview.indices %}
| {{index.name}} | {{index.value}} | {{index.change}} | {{index.change_percent}}% |
{% endfor %}
{% endif %}

## Analysis Results

{% if data.stock_analysis %}
### Individual Stock Analysis

{% for stock in data.stock_analysis %}
#### {{stock.symbol}} - {{stock.name}}

**Current Price:** ${{stock.current_price}}
**Target Price:** ${{stock.target_price}}
**Recommendation:** {{stock.recommendation | upper}}

##### Technical Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
{% for indicator in stock.technical_indicators %}
| {{indicator.name}} | {{indicator.value}} | {{indicator.signal}} |
{% endfor %}

##### Fundamental Metrics
{% if stock.fundamentals %}
| Metric | Value | Industry Avg |
|--------|-------|--------------|
| P/E Ratio | {{stock.fundamentals.pe_ratio}} | {{stock.fundamentals.industry_pe}} |
| ROE | {{stock.fundamentals.roe}}% | {{stock.fundamentals.industry_roe}}% |
| Debt/Equity | {{stock.fundamentals.debt_equity}} | {{stock.fundamentals.industry_debt_equity}} |
{% endif %}

##### Risk Assessment
- **Volatility:** {{stock.risk.volatility}}%
- **Beta:** {{stock.risk.beta}}
- **Risk Score:** {{stock.risk.score}}/100

{{stock.analysis_summary}}

---
{% endfor %}
{% endif %}

{% if data.portfolio_analysis %}
### Portfolio Analysis

**Total Value:** ${{data.portfolio_analysis.total_value}}
**Total Return:** {{data.portfolio_analysis.total_return}}%
**Risk Score:** {{data.portfolio_analysis.risk_score}}/100

#### Asset Allocation
| Asset | Symbol | Weight | Value | Return |
|-------|--------|--------|-------|--------|
{% for asset in data.portfolio_analysis.assets %}
| {{asset.name}} | {{asset.symbol}} | {{asset.weight}}% | ${{asset.value}} | {{asset.return}}% |
{% endfor %}

#### Performance Metrics
- **Annualized Return:** {{data.portfolio_analysis.performance.annualized_return}}%
- **Volatility:** {{data.portfolio_analysis.performance.volatility}}%
- **Sharpe Ratio:** {{data.portfolio_analysis.performance.sharpe_ratio}}
- **Max Drawdown:** {{data.portfolio_analysis.performance.max_drawdown}}%
{% endif %}

## Sentiment Analysis

{% if data.sentiment_analysis %}
**Overall Market Sentiment:** {{data.sentiment_analysis.overall_sentiment}}
**News Sentiment Score:** {{data.sentiment_analysis.news_score}}/100
**Social Media Sentiment:** {{data.sentiment_analysis.social_score}}/100

### Key News Items
{% for news in data.sentiment_analysis.news_items %}
- **{{news.title}}** ({{news.source}})
  Sentiment: {{news.sentiment}} | Impact: {{news.impact}}
{% endfor %}
{% endif %}

## Risk Management

{% if data.risk_management %}
### Risk Metrics
| Metric | Current Value | Threshold | Status |
|--------|---------------|-----------|--------|
{% for risk in data.risk_management.metrics %}
| {{risk.name}} | {{risk.current_value}} | {{risk.threshold}} | {{risk.status}} |
{% endfor %}

### Risk Alerts
{% for alert in data.risk_management.alerts %}
- **{{alert.level | upper}}:** {{alert.message}}
{% endfor %}

### Position Sizing Recommendations
{% for position in data.risk_management.position_sizing %}
- **{{position.symbol}}:** {{position.recommended_size}}% of portfolio (Current: {{position.current_size}}%)
{% endfor %}
{% endif %}

## Investment Recommendations

{% if data.recommendations %}
{% for rec in data.recommendations %}
### {{rec.title}}

**Action:** {{rec.action | upper}}
**Priority:** {{rec.priority}}
**Confidence Level:** {{rec.confidence}}%

{{rec.description}}

#### Rationale
{% for reason in rec.rationale %}
- {{reason}}
{% endfor %}

#### Risk Considerations
{% for risk in rec.risks %}
- {{risk}}
{% endfor %}

{% if rec.expected_return %}
**Expected Return:** {{rec.expected_return}}%
**Time Horizon:** {{rec.time_horizon}}
{% endif %}

---
{% endfor %}
{% endif %}

## Backtesting Results

{% if data.backtesting %}
### Strategy Performance

**Strategy:** {{data.backtesting.strategy_name}}
**Backtest Period:** {{data.backtesting.start_date}} to {{data.backtesting.end_date}}

#### Performance Summary
- **Total Return:** {{data.backtesting.total_return}}%
- **Annualized Return:** {{data.backtesting.annualized_return}}%
- **Volatility:** {{data.backtesting.volatility}}%
- **Sharpe Ratio:** {{data.backtesting.sharpe_ratio}}
- **Maximum Drawdown:** {{data.backtesting.max_drawdown}}%
- **Win Rate:** {{data.backtesting.win_rate}}%

#### Risk Metrics
- **Beta:** {{data.backtesting.beta}}
- **Alpha:** {{data.backtesting.alpha}}%
- **Sortino Ratio:** {{data.backtesting.sortino_ratio}}
- **Calmar Ratio:** {{data.backtesting.calmar_ratio}}

{% if data.backtesting.trades %}
#### Trade Summary
- **Total Trades:** {{data.backtesting.trades.total}}
- **Winning Trades:** {{data.backtesting.trades.wins}}
- **Losing Trades:** {{data.backtesting.trades.losses}}
- **Average Win:** {{data.backtesting.trades.avg_win}}%
- **Average Loss:** {{data.backtesting.trades.avg_loss}}%
{% endif %}
{% endif %}

## Market Commentary

{% if data.market_commentary %}
{{data.market_commentary}}
{% endif %}

## Disclaimers and Risk Warnings

{% if data.disclaimers %}
{% for disclaimer in data.disclaimers %}
**{{disclaimer.title}}:** {{disclaimer.text}}
{% endfor %}
{% else %}
**Investment Risk Warning:** All investments carry risk of loss. Past performance does not guarantee future results. This analysis is for informational purposes only and should not be considered as investment advice. Please consult with a qualified financial advisor before making investment decisions.

**Data Accuracy:** This report is based on publicly available data and algorithmic analysis. While we strive for accuracy, we cannot guarantee the completeness or correctness of all information presented.

**Not Financial Advice:** This report is generated by an automated system and should not be considered as personalized financial advice. Investment decisions should be based on your individual financial situation and goals.
{% endif %}

## Technical Details

{% if data.technical_details %}
**Analysis Engine Version:** {{data.technical_details.version}}
**Data Sources:** {{data.technical_details.data_sources | join(', ')}}
**Analysis Models:** {{data.technical_details.models | join(', ')}}
**Generation Time:** {{data.technical_details.generation_time}}
**Data Freshness:** {{data.technical_details.data_age}}
{% endif %}

---

*This report was generated by the Agent Investment Platform on {{data.analysis_date}}*
*Report ID: {{data.report_id}}*
*Next Update: {{data.next_update}}*

{% if data.contact_info %}
*For questions or feedback, contact: {{data.contact_info}}*
{% endif %}
