# Agent Investment Platform - AI Memory Bank

## Project Context & Overview

**Project Name**: Agent Investment Platform  
**Owner**: eightbitreaper  
**Repository**: https://github.com/eightbitreaper/agent-investment-platform  
**Purpose**: AI-powered stock investment analysis platform with real-time insights and automated reporting

### Project Goals
- Create one-command setup for contributors via VS Code agent
- Provide automated analysis of stocks, ETFs, and bonds
- Generate markdown reports with buy/sell/hold recommendations
- Support both local LLMs (privacy) and API-based LLMs (performance)
- Maintain comprehensive documentation and contributor-friendly onboarding

### Architecture Decisions
- **MCP Server Infrastructure** using Model Context Protocol for AI agent communication
- **Production-ready MCP servers** (4 specialized servers with 20+ financial tools)
- **Python-based backend** with comprehensive financial data integration
- **Docker containerization** for cross-platform deployment
- **Configuration-driven** approach with external JSON configuration files

## User Profile & Preferences

### Working Style
- **Systematic approach**: Prefers breaking down complex tasks into manageable sub-tasks
- **Documentation-focused**: Values well-organized documentation structure
- **Quality-oriented**: Emphasizes proper file organization and cross-referencing
- **Collaboration-minded**: Wants easy onboarding for new contributors

### Code Preferences
- **Clear file organization**: Docs in `docs/`, scripts in `scripts/`, source in `src/`
- **Comprehensive comments**: Detailed docstrings and inline documentation
- **Error handling**: Robust exception handling with informative messages
- **Cross-platform compatibility**: Windows/Linux/macOS support

### Communication Style
- **Appreciates detailed explanations** with technical context
- **Likes progress updates** and clear completion status
- **Values proactive suggestions** for improvements
- **Prefers structured responses** with clear sections and formatting

## Project Evolution & Key Decisions

### Session 1 (September 21, 2025)
**Major Accomplishments:**
- Established comprehensive task breakdown (48 detailed sub-tasks)
- Created VS Code agent initialization system
- Implemented master development guidelines system
- Built cross-platform dependency installer
- Created comprehensive environment configuration

**Key Technical Decisions:**
1. **Guidelines System**: Created `.vscode/guidelines.prompt.md` with `alwaysApply: true` for automatic enforcement
2. **Documentation Structure**: All markdown files in `docs/` with README branching structure  
3. **Initialization Strategy**: One-command setup via `@workspace run docs/setup/initialize.prompt`
4. **Configuration Approach**: Environment variables + YAML configs for maximum flexibility

**User Feedback & Patterns:**
- Emphasized importance of proper documentation organization
- Requested mandatory guidelines reference in task instructions
- Valued automatic VS Code agent discovery of prompt files
- Appreciated comprehensive, production-ready implementations

## Current Task Status

### Completed Tasks ✅
- **0.1**: `docs/setup/initialize.prompt.md` - VS Code agent setup instructions
- **0.2**: `scripts/initialize.py` - Main initialization orchestrator  
- **0.3**: `scripts/setup/install-dependencies.py` - Cross-platform dependency installer
- **0.4**: `scripts/setup/configure-environment.py` - Environment configuration automation

### Next Priority Tasks 🎯
- **0.5**: `scripts/setup/download-models.py` - Local LLM model management
- **0.6**: `scripts/setup/validate-setup.py` - Setup verification system
- **0.7**: `.vscode/tasks.json` - VS Code workspace tasks
- **0.8**: `.vscode/settings.json` - VS Code workspace settings
- **0.9**: Update `README.md` as main entry point

### Long-term Goals 🚀
- Complete VS Code Agent Initialization System (Tasks 0.0)
- Build MCP Server Integration (Tasks 2.0)
- Implement Analysis Engine (Tasks 3.0)
- Create Report Generation System (Tasks 4.0)

## Technical Knowledge Accumulated

### Platform Architecture
```
Data Sources → MCP Servers → Analysis Engine → Report Generator → GitHub
     ↓              ↓             ↓              ↓           ↓
Stock APIs    Stock Agent   Sentiment      Markdown    Version Control
News Feeds    News Agent    Technical      Templates   Report History  
YouTube       YT Agent      Strategy       LLM Gen     Notifications
```

### Key Technologies
- **MCP (Model Context Protocol)**: For agent communication
- **Docker & Docker Compose**: Containerized deployment
- **Ollama**: Local LLM hosting (privacy-focused)
- **OpenAI/Anthropic APIs**: Cloud LLM options
- **GitHub Integration**: Report version control and project hosting
- **YAML/JSON Configuration**: External configuration management

### Critical Implementation Patterns
1. **Error Handling**: Comprehensive try/catch with informative logging
2. **Platform Detection**: OS-specific installation and configuration
3. **Configuration Templates**: Example files with environment variable substitution
4. **Modular Design**: Separate scripts for different setup phases
5. **Interactive Setup**: User-guided configuration with sensible defaults

## Relationship Dynamics

### What Works Well
- **Detailed technical implementations** with full production features
- **Comprehensive documentation** and cross-referencing
- **Proactive quality suggestions** and best practices
- **Systematic task progression** with clear completion criteria

### User Expectations
- **Follow guidelines religiously** - Documentation organization is critical
- **Provide complete implementations** - No partial or placeholder code
- **Update task status immediately** after completion
- **Maintain consistency** with established patterns and decisions

### Communication Effectiveness
- **Use clear status indicators** (✅ ❌ 🎯 ⚡)
- **Provide implementation summaries** after each task
- **Ask for explicit permission** before proceeding to next task
- **Highlight key features** and architectural decisions

## Future Session Preparation

### Context to Remember
1. **Guidelines are mandatory** - Always reference `.vscode/guidelines.prompt.md`
2. **Documentation goes in docs/** - Never in project root except README.md
3. **Task updates required** - Mark completed tasks in `tasks/tasks-prd.md`
4. **User prefers comprehensive implementations** - Full production-ready code

### Key Files to Reference
- **Task List**: `tasks/tasks-prd.md` - Current progress and next steps
- **Guidelines**: `.vscode/guidelines.prompt.md` - Development standards
- **Project Docs**: `docs/README.md` - Documentation navigation
- **Main README**: `README.md` - Project entry point

### Continuation Strategy
- **Resume from next uncompleted task** in sequence
- **Reference this memory bank** for context and patterns
- **Maintain established code quality** and documentation standards
- **Continue systematic task-by-task progression** with user approval

---

*This memory bank will be updated after each session to maintain continuity and improve collaboration effectiveness.*