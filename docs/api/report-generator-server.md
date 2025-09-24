# Report Generator Server Documentation

The Report Generator MCP Server automates the creation and publishing of comprehensive investment analysis reports with GitHub integration and chart generation capabilities.

## Overview

**Location**: `src/mcp_servers/report_generator_server.py`
**Port**: 3005
**Protocol**: MCP over stdio
**Dependencies**: GitHub API, Chart generation libraries

## Features

### 📝 Report Generation
- Automated investment analysis reports
- Customizable report templates (Jinja2)
- Multi-format output (Markdown, HTML, PDF)
- Dynamic chart and graph integration

### 📊 Chart Generation
- Financial charts and visualizations
- Technical analysis charts with indicators
- Performance comparison charts
- Portfolio allocation visualizations

### 🐙 GitHub Integration
- Automatic report publishing to GitHub repositories
- Commit and push automation
- Issue and PR creation for report reviews
- Repository organization and archiving

### 📋 Template Management
- Customizable report templates
- Theme and styling options
- Dynamic content sections
- Conditional content rendering

## Available Tools

### generate_investment_report(data, template, format)
Generate a comprehensive investment analysis report.

**Parameters**:
- `data` (object): Analysis data and metrics
- `template` (string): Report template name
- `format` (string): Output format (markdown, html, pdf)

**Response**: Generated report content and metadata

### publish_to_github(report, repository, branch)
Publish report to GitHub repository.

**Parameters**:
- `report` (object): Report content and metadata
- `repository` (string): Target GitHub repository
- `branch` (string): Branch for publication

**Response**: GitHub commit information and URL

### create_charts(data, chart_types, style)
Generate financial charts and visualizations.

**Parameters**:
- `data` (object): Chart data and parameters
- `chart_types` (array): Types of charts to generate
- `style` (string): Chart styling theme

**Response**: Generated chart files and metadata

### format_markdown(content, template, options)
Format content using Markdown templates.

**Parameters**:
- `content` (object): Content to format
- `template` (string): Markdown template
- `options` (object): Formatting options

**Response**: Formatted Markdown content

### manage_templates(action, template_data)
Manage report templates.

**Parameters**:
- `action` (string): Action to perform (create, update, delete, list)
- `template_data` (object): Template content and metadata

**Response**: Template management results

## Report Templates

### Standard Investment Report
Comprehensive analysis including:
- Executive summary and key findings
- Technical analysis with charts
- Fundamental analysis and valuation
- Risk assessment and recommendations
- Market context and sector analysis

### Portfolio Analysis Report
Portfolio-focused analysis including:
- Portfolio composition and allocation
- Performance metrics and benchmarking
- Risk analysis and diversification
- Rebalancing recommendations
- Individual position analysis

### Market Research Report
Market-wide analysis including:
- Market overview and trends
- Sector performance analysis
- Economic indicators and impact
- Market sentiment analysis
- Investment opportunities and risks

## Configuration

Server configuration in `config/report-config.yaml`:

```yaml
github:
  token: "${GITHUB_TOKEN}"
  default_repo: "${GITHUB_REPO}"
  commit_author: "Investment Platform Bot"
  commit_email: "bot@investment-platform.com"

templates:
  directory: "templates/reports"
  default_template: "investment_analysis.md"
  custom_templates:
    - portfolio_analysis.md
    - market_research.md
    - risk_assessment.md

charts:
  library: "plotly"
  default_theme: "financial"
  output_format: ["png", "svg", "html"]
  dimensions:
    width: 1200
    height: 800

reports:
  output_directory: "reports"
  archive_after_days: 90
  max_file_size: "10MB"
```

## Development Usage

### Running the Server

**Standalone Mode**:
```bash
python -m src.mcp_servers.report_generator_server
```

**Docker Mode**:
```bash
docker-compose up mcp-report-server -d
```

### Testing Tools

Test report generation:

```bash
# Test report generation
curl -X POST http://localhost:3005/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "generate_investment_report",
    "params": {
      "data": {
        "symbol": "AAPL",
        "analysis": "comprehensive",
        "timeframe": "1y"
      },
      "template": "investment_analysis",
      "format": "markdown"
    }
  }'

# Test GitHub publishing
curl -X POST http://localhost:3005/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "publish_to_github",
    "params": {
      "report": {"content": "# Investment Report..."},
      "repository": "investment-reports",
      "branch": "main"
    }
  }'
```

## Chart Generation

### Supported Chart Types

**Price Charts**:
- Candlestick charts with volume
- Line charts for price trends
- Moving averages and indicators

**Technical Analysis Charts**:
- RSI, MACD, Bollinger Bands
- Support and resistance levels
- Volume and momentum indicators

**Fundamental Charts**:
- Financial ratio comparisons
- Peer analysis charts
- Valuation metric trends

**Portfolio Charts**:
- Asset allocation pie charts
- Performance comparison charts
- Risk-return scatter plots

### Chart Customization

```python
chart_config = {
    "theme": "financial",
    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c"],
    "grid": True,
    "legend": {"position": "top"},
    "title": {"size": 16, "weight": "bold"}
}
```

## GitHub Integration

### Repository Structure
Reports are organized in GitHub repositories with this structure:

```
investment-reports/
├── daily/
│   ├── 2024-09-23-market-analysis.md
│   └── 2024-09-23-portfolio-review.md
├── weekly/
│   └── 2024-09-W38-sector-analysis.md
├── monthly/
│   └── 2024-09-monthly-summary.md
└── charts/
    ├── AAPL-technical-analysis.png
    └── portfolio-allocation.png
```

### Automated Publishing Workflow

1. Generate report content and charts
2. Create GitHub branch (optional)
3. Commit files to repository
4. Create pull request for review (optional)
5. Merge to main branch
6. Archive old reports

## Template System

### Template Structure

```markdown
# {{ report.title }}

**Generated**: {{ report.timestamp }}
**Symbol**: {{ data.symbol }}
**Analysis Period**: {{ data.timeframe }}

## Executive Summary
{{ analysis.summary }}

## Technical Analysis
{% if analysis.technical %}
{{ analysis.technical.description }}

![Technical Chart]({{ charts.technical_chart }})
{% endif %}

## Recommendations
{% for recommendation in analysis.recommendations %}
- **{{ recommendation.action }}**: {{ recommendation.reasoning }}
{% endfor %}
```

### Custom Template Variables

- `data.*` - Input analysis data
- `analysis.*` - Analysis results
- `charts.*` - Generated chart references
- `report.*` - Report metadata
- `config.*` - Configuration values

## Debugging

### Common Issues

**GitHub Authentication Failed**:
1. Verify GitHub token permissions
2. Check repository access rights
3. Validate token expiration

**Chart Generation Failed**:
1. Check chart library installation
2. Verify data format and completeness
3. Monitor memory usage for large datasets

**Template Rendering Error**:
1. Validate template syntax
2. Check variable availability
3. Test with minimal data set

### Debug Mode

Enable comprehensive logging:

```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
python -m src.mcp_servers.report_generator_server
```

## Use Cases

### Automated Daily Reports
- Generate daily market analysis reports
- Publish to GitHub for team access
- Include technical and fundamental analysis

### Portfolio Reporting
- Create comprehensive portfolio reviews
- Track performance against benchmarks
- Generate rebalancing recommendations

### Research Documentation
- Document investment research and decisions
- Archive analysis for future reference
- Share insights with team members

## Related Documentation

- [MCP Server Overview](mcp-overview.md) - Understanding MCP architecture
- [Analysis Engine Server](analysis-engine-server.md) - Investment analysis capabilities
- [GitHub Integration Guide](../setup/github-configuration.md) - Setting up GitHub access
- [Template Development](../development/template-development.md) - Creating custom templates
