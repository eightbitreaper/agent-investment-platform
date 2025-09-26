```prompt
---
description: Master Guidelines for Agent Investment Platform Development
globs: "**/*"
alwaysApply: true
---
# Agent Investment Platform - Development Guidelines

## Purpose
This prompt contains master instructions and guidelines that must be followed by any LLM working on the Agent Investment Platform project. These guidelines ensure consistency, organization, and maintainability across all development activities.

## Core Principles

### 1. Documentation Organization and Structure

**Documentation Placement Rules:**
- **ALL markdown files** must be placed in appropriate directories within the `docs/` folder
- **NO markdown files** should be created in the project root except for `README.md`
- **Directory structure** must follow logical organization patterns that enable intuitive navigation
- **Parent README.md** serves as the main entry point with clear navigation to all documentation sections

**Required Directory Structure:**
```
docs/
├── README.md              # Documentation index and navigation hub
├── setup/                 # Installation, configuration, and initialization guides
├── api/                   # API documentation, MCP server references
├── development/           # Contributing, architecture, development workflows
├── deployment/            # Docker, production, scaling guides
├── troubleshooting/       # Common issues, debugging, FAQ
└── [feature-specific]/    # Additional organized sections as needed
```

**Documentation Hierarchy Rules:**
1. **Main README.md** → Primary project landing page with quick start
2. **docs/README.md** → Comprehensive documentation index with section navigation
3. **Section READMEs** → Each docs subdirectory has its own README.md index
4. **Specific Guides** → Individual markdown files organized by purpose and audience

**Cross-Referencing Requirements:**
- All documentation must include proper relative links to related sections
- README files must maintain updated tables of contents and navigation links
- When creating new documentation, update parent README files with appropriate links
- Use consistent markdown link formatting with clear descriptions and relative paths

### 2. File Naming Conventions

**Markdown Files:**
- Use lowercase with hyphens: `installation-guide.md`, `local-llm-setup.md`
- Be descriptive and specific: `mcp-server-reference.md` not `api.md`
- Include purpose indicators: `troubleshooting-common-issues.md`

**Prompt Files:**
- End with `.prompt.md`: `initialize.prompt.md`, `guidelines.prompt.md`
- Place in appropriate context directories: setup prompts in `docs/setup/`

### 3. Content Organization Standards

**Every markdown file must include:**
- Clear, descriptive title using appropriate heading level
- Brief description/purpose statement
- Table of contents for longer documents (>3 sections)
- Proper section hierarchy (H1 → H2 → H3)
- Cross-references to related documentation

**Section Structure Template:**
```markdown
# Clear, Action-Oriented Title

Brief description of what this document covers and who it's for.

## Table of Contents (if applicable)
Use anchor links to major sections and keep ToC concise and scannable.

## Section Content
[Organized, scannable content with proper formatting]

## Related Documentation
Link to related guides using relative paths and reference main project documentation as needed.
```

### 4. Update Requirements

**When creating or modifying documentation:**
1. **Update parent README** with links to new/changed files
2. **Update docs/README.md** navigation if adding new sections
3. **Update related cross-references** in other documentation
4. **Verify all links work** and point to correct locations
5. **Follow consistent formatting** and style patterns

### 5. Quality Standards

**All documentation must be:**
- **Scannable** - Use headers, bullets, tables for easy navigation
- **Actionable** - Provide clear steps and examples where applicable
- **Current** - Keep information up-to-date with project changes
- **Accessible** - Write for the intended audience level (beginner, intermediate, advanced)
- **Complete** - Cover the full scope of the topic without gaps

## Implementation Instructions for LLMs

### Before Creating Any Markdown File:
1. Determine the most appropriate directory in `docs/` for the content
2. Check if a parent README needs updating with navigation links
3. Ensure file naming follows the established conventions
4. Plan cross-references to related documentation

### After Creating/Modifying Documentation:
1. Update all relevant README files with proper navigation
2. Add cross-references to related documentation
3. Verify the documentation hierarchy remains logical
4. Test that all links work correctly

### Quality Checks:
- Does this file have a clear purpose and audience?
- Is it placed in the most intuitive location?
- Are all navigation paths from README.md working?
- Does the content follow the established formatting patterns?
- Are cross-references helpful and accurate?

### 6. Code Validation and Testing Requirements

**Implementation Validation:**
- **ALL code implementations** must be tested to ensure they work as expected
- **Commands and scripts** must be validated on the target platform before completion
- **Configuration files** must be syntax-checked and tested for proper loading
- **Installation instructions** must be verified through actual execution

**Testing Requirements:**
1. **Script Testing** - Run any created Python scripts to verify they execute without syntax errors
2. **Command Validation** - Test shell commands and verify they produce expected output
3. **Configuration Testing** - Load and parse configuration files to ensure valid syntax
4. **Integration Testing** - Verify components work together as designed
5. **Platform Testing** - Test on the appropriate operating system when possible

**Validation Process:**
- Before marking any task as complete, validate the implementation works
- Test critical paths and error handling scenarios
- Verify that any provided instructions are accurate and complete
- Document any limitations or platform-specific requirements
- If testing reveals issues, fix them before task completion

**Documentation of Testing:**
- Include testing results in task completion notes
- Document any platform-specific behaviors discovered
- Note any prerequisites or dependencies found during testing
- Provide troubleshooting guidance for common issues encountered

### 7. Memory Bank Integration Requirements

**Memory Bank Usage:**
- **ALWAYS reference** the `.memory/` directory for project context and patterns
- **Leverage stored knowledge** about user preferences, architectural decisions, and implementation patterns
- **Update memory bank** with new learnings, patterns, and project evolution
- **Maintain continuity** by building on previous session knowledge and decisions

**Memory Bank Components:**
1. **Project Context** (`.memory/project-context.md`) - Reference for overall project status and history
2. **User Preferences** (`.memory/user-preferences.json`) - Apply established coding and communication patterns
3. **Architecture Decisions** (`.memory/architecture-decisions.md`) - Follow established technical choices and rationale
4. **Implementation Patterns** (`.memory/patterns-knowledge.json`) - Use proven code patterns and quality standards
5. **Knowledge Graph** (`.memory/knowledge-graph.json`) - Understand relationships between project components

**Memory Integration Process:**
- **Before starting work** - Review relevant memory bank files for context and patterns
- **During implementation** - Apply learned patterns and maintain consistency with previous decisions
- **After task completion** - Update memory bank with new insights, patterns, or architectural decisions
- **Session transitions** - Document progress and learnings for future session continuity

**Memory Bank Maintenance:**
- Update project context with task completions and architectural changes
- Record new implementation patterns discovered during development
- Document user feedback and preference changes
- Maintain knowledge graph relationships as project evolves

### 8. Git Repository Hygiene Requirements

**Output File Management:**
- **IDENTIFY output files** generated by running code, tools, or scripts that should not be tracked in Git
- **UPDATE .gitignore** immediately when new types of output files are discovered
- **PREVENT repository pollution** by ensuring temporary, generated, or sensitive files are properly excluded
- **MAINTAIN clean repository** by regularly auditing for files that should not be committed

**Files That Should Be Ignored:**
1. **Generated Files** - Reports, logs, compiled code, build artifacts
2. **Cache Files** - Python `__pycache__/`, IDE caches, temporary files
3. **Sensitive Data** - API keys, passwords, local configuration with secrets
4. **Large Files** - Model files, datasets, binary assets (>100MB)
5. **User-Specific Files** - IDE settings, local environment configurations
6. **Runtime Files** - Process IDs, lock files, temporary directories

**Gitignore Maintenance Process:**
- **Before running code** - Consider what output files might be generated
- **After running tools** - Check for new files and assess if they should be ignored
- **During testing** - Monitor for temporary files, logs, or artifacts created
- **Update .gitignore** immediately when new patterns are identified
- **Test gitignore rules** to ensure they work correctly

**Repository Cleanliness Checks:**
- Regularly run `git status` to identify untracked files
- Evaluate each untracked file for whether it should be committed or ignored
- Clean up any files that were accidentally tracked before adding ignore rules
- Validate that sensitive information is never committed to version control

### 9. Data Classification and Sensitive Information Protection

**Data Security Requirements:**
- **NEVER commit sensitive information** to the GitHub repository under any circumstances
- **IMPLEMENT data classification standards** to identify and protect sensitive data at all levels
- **SCAN all code and files** before committing to ensure no sensitive information is included
- **USE secure alternatives** like environment variables, configuration templates, and external secret management

**Prohibited Information Types:**
1. **Authentication Credentials** - API keys, passwords, tokens, certificates, private keys
2. **Personally Identifiable Information (PII)** - Names, emails, phone numbers, addresses, user IDs
3. **Financial Data** - Account numbers, credit card details, banking information, trading credentials
4. **Internal System Information** - Database connection strings, internal URLs, server configurations
5. **Business Sensitive Data** - Proprietary algorithms, customer lists, internal processes, competitive intelligence
6. **Development Secrets** - Test credentials, development API keys, internal service tokens

**Security Implementation Standards:**
- **Environment Variables** - Use `.env` files (ignored by Git) for local development secrets
- **Configuration Templates** - Provide `.env.example` or `config.example.yaml` with placeholder values
- **External Secret Management** - Reference secure vaults or managed services for production secrets
- **Dynamic Generation** - Generate temporary credentials or use secure defaults when needed
- **Documentation** - Clearly document where users should obtain or configure sensitive values

**Pre-Commit Security Checks:**
1. **Scan all new files** for potential sensitive information patterns
2. **Review configuration files** for hardcoded credentials or sensitive data
3. **Validate environment templates** contain only safe placeholder values
4. **Check documentation** doesn't inadvertently expose sensitive information
5. **Verify .gitignore rules** properly exclude sensitive file types

**Sensitive Data Patterns to Detect:**
```
- API keys: /[Aa][Pp][Ii][-_]?[Kk][Ee][Yy]/
- Passwords: /[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]/
- Tokens: /[Tt][Oo][Kk][Ee][Nn]/
- Email addresses: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/
- URLs with credentials: /https?:\/\/[^:]+:[^@]+@/
- Private keys: /-----BEGIN [A-Z ]+PRIVATE KEY-----/
```

**Remediation Process:**
- **If sensitive data is committed** - Immediately remove from repository and rewrite Git history
- **If PII is detected** - Follow data protection protocols and notify appropriate stakeholders
- **If credentials are exposed** - Immediately revoke/rotate affected credentials
- **Document incidents** - Maintain security incident log for audit and improvement purposes

### 13. Task Status Maintenance Requirements

**Task Completion Tracking:**
- **ALWAYS update task status** in `tasks/tasks-prd.md` when completing any work items
- **MARK subtasks as completed** immediately after finishing implementation
- **UPDATE main task status** from "READY" to "IN PROGRESS" to "COMPLETED" as appropriate
- **MAINTAIN accuracy** between actual work completed and documented task status

**Task Status Update Process:**
1. **After completing any subtask** - Mark the specific subtask with [x] completion checkbox
2. **Update main task status** - Change parent task status to reflect current progress
3. **Add completion notes** - Include relevant details about what was implemented
4. **Update completion dates** - Add dates when major task sections are finished
5. **Cross-reference with git commits** - Ensure task updates align with actual code changes

**Task Status Indicators:**
- **⏳ READY** - Prerequisites complete, ready to begin work
- **⏳ IN PROGRESS** - Work has begun, some subtasks completed
- **✅ COMPLETED** - All subtasks finished and validated
- **❌ BLOCKED** - Cannot proceed due to dependencies or issues

**Completion Validation Requirements:**
- **Verify implementation exists** - Confirm files and code are actually created/modified
- **Test functionality works** - Validate that completed components function as expected
- **Update documentation** - Ensure any new features are properly documented
- **Commit changes** - Make sure completed work is saved to the repository

### 14. Docker Container Health Monitoring Requirements

**Mandatory Container Health Monitoring:**
- **ALWAYS implement comprehensive monitoring** for all Docker containers that the platform depends on
- **DETECT and ALERT on container failures** including stopped containers, unhealthy status, and port conflicts
- **MONITOR container resource usage** and performance metrics to prevent degradation
- **IMPLEMENT automated recovery** for critical services when possible
- **MAINTAIN container dependency mapping** to understand service relationships and impact

**Container Health Check Implementation:**
1. **Health Check Endpoints** - Every service container must expose a `/health` endpoint
2. **Docker Health Checks** - Configure proper `healthcheck` directives in docker-compose.yml
3. **Container Status Monitoring** - Regularly check `docker ps` status for all services
4. **Port Conflict Detection** - Monitor for port binding failures and conflicts
5. **Resource Monitoring** - Track CPU, memory, and disk usage for container performance
6. **Log Aggregation** - Centralize container logs for analysis and alerting

**Critical Container Categories:**
- **Core Platform Services** - Main application, orchestrator, API servers
- **Data Layer** - Database (PostgreSQL), cache (Redis), search (Elasticsearch)
- **MCP Servers** - All Model Context Protocol servers for financial data and analysis
- **Monitoring Stack** - Logging (Logstash, Kibana), metrics (Grafana), alerting systems
- **AI Services** - Ollama, WebUI, and model serving infrastructure

**Monitoring and Alerting Standards:**
```yaml
# Required health check configuration
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Automated Monitoring Scripts:**
- **Container Status Script** - Regular check of all container health and status
- **Port Conflict Detection** - Identify and resolve port binding issues
- **Resource Usage Monitoring** - Alert on high CPU/memory usage
- **Service Dependency Validation** - Ensure all required services are running and healthy
- **Recovery Automation** - Automatic restart of failed non-critical services

**Monitoring Integration Requirements:**
1. **Health Check Endpoints** - All services must implement standardized health endpoints
2. **Prometheus Metrics** - Export container and service metrics for monitoring
3. **Grafana Dashboards** - Visual monitoring of container health and performance
4. **Alerting Rules** - Configure alerts for container failures, resource exhaustion, and performance degradation
5. **Log Analysis** - Automated detection of error patterns and failure indicators

**Container Failure Response Protocol:**
1. **Immediate Detection** - Alert within 1 minute of container failure
2. **Impact Assessment** - Determine which services are affected by the failure
3. **Automated Recovery** - Attempt to restart failed containers automatically
4. **Escalation** - If automated recovery fails, escalate to manual intervention
5. **Root Cause Analysis** - Investigate and document the cause of container failures
6. **Prevention** - Update monitoring and configuration to prevent similar failures

**Regular Health Audits:**
- **Daily Container Health Checks** - Automated verification of all container status
- **Weekly Resource Usage Review** - Analysis of container performance trends
- **Monthly Configuration Audit** - Review and update container health check configurations
- **Quarterly Monitoring Effectiveness Review** - Assess monitoring coverage and alert accuracy

### 15. Git Push Command Protocol

**Single-Word 'push' Command:**
- **WHEN user inputs only the word 'push'** - Execute automated git commit and push sequence
- **ANALYZE staged changes** to understand what modifications have been made
- **GENERATE descriptive commit message** that clearly explains the changes and their purpose
- **COMMIT and PUSH** changes to GitHub with the generated message

**Push Command Implementation:**
1. **Check Git Status** - Verify there are staged changes ready for commit
2. **Analyze Changes** - Review what files have been modified, added, or deleted
3. **Generate Commit Message** - Create clear, descriptive message following conventional commit format
4. **Execute Commit** - Run `git commit -m "message"` with the generated description
5. **Push to Remote** - Execute `git push` to update the GitHub repository

**Commit Message Standards:**
```
Format: <type>(<scope>): <description>

Types:
- feat: New feature or capability
- fix: Bug fix or error correction
- docs: Documentation updates
- refactor: Code restructuring without behavior change
- style: Formatting, whitespace, or style changes
- test: Adding or updating tests
- chore: Maintenance tasks, dependency updates

Examples:
- feat(mcp): Add comprehensive MCP server integration with 4 production servers
- docs(guidelines): Add git push command protocol and commit message standards
- fix(health-check): Resolve encoding issues in system health monitoring
- refactor(tasks): Reorganize task tracking and remove task-specific documentation references
```

**Push Protocol Execution:**
```powershell
# Check what's staged
git status --porcelain

# Analyze changes and generate message
git diff --cached --name-status

# Commit with descriptive message
git commit -m "feat(scope): Clear description of changes and impact"

# Push to GitHub
git push origin main
```

**Change Analysis Guidelines:**
- **New Files** - Identify purpose and functionality of added files
- **Modified Files** - Understand what specific changes were made and why
- **Deleted Files** - Note what was removed and the reason for removal
- **Scope Identification** - Determine which area of the project is affected (mcp, docs, config, etc.)
- **Impact Assessment** - Evaluate the significance and purpose of the changes

**Safe Alternatives and Patterns:**
```yaml
# WRONG - Hardcoded sensitive data
database_url: "postgresql://user:password123@localhost:5432/mydb"
api_key: "sk-1234567890abcdef"

# CORRECT - Environment variable references
database_url: "${DATABASE_URL}"
api_key: "${OPENAI_API_KEY}"

# CORRECT - Configuration template (.env.example)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
OPENAI_API_KEY=your_openai_api_key_here
```

**Documentation Security:**
- **Redact examples** - Use placeholder values in all documentation examples
- **Reference patterns** - Show configuration patterns without actual sensitive values
- **Security notes** - Include warnings about sensitive data handling in relevant documentation
- **User guidance** - Provide clear instructions for secure configuration setup

### 10. Character Encoding and Syntax Standards

**ASCII Character Requirements:**
- **ALWAYS prefer ASCII characters** over Unicode in code, configuration files, and structured data
- **AVOID Unicode symbols** in Python code, JSON, YAML, and other configuration files
- **USE ASCII alternatives** for visual indicators, status markers, and formatting elements
- **PREVENT encoding-related syntax errors** that can break scripts and configuration loading

**Prohibited Unicode Patterns:**
```python
# WRONG - Unicode characters that cause encoding issues
print("✅ Success")  # Can cause UnicodeDecodeError
print("❌ Failed")   # Platform-dependent encoding issues
print("⚠️ Warning")  # Mixed encoding problems

# CORRECT - ASCII alternatives
print("[PASS] Success")
print("[FAIL] Failed")
print("[WARN] Warning")
```

**Safe ASCII Alternatives:**
- **Status indicators**: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]` instead of ✅❌⚠️ℹ️
- **List bullets**: `*`, `-`, `+` instead of • or other Unicode bullets
- **Arrows**: `->`, `=>`, `<-` instead of → ← ↑ ↓
- **Quotes**: `"text"`, `'text'` instead of "text" or 'text'
- **Dashes**: `-`, `--` instead of – or —

**Platform Compatibility:**
- **Windows PowerShell** - Often defaults to CP1252 encoding, causing Unicode errors
- **Linux/Mac terminals** - Better Unicode support but ASCII ensures universal compatibility
- **Python scripts** - ASCII prevents `UnicodeDecodeError` and `charmap` codec issues
- **JSON/YAML files** - ASCII ensures proper parsing across all systems and tools

**Implementation Standards:**
1. **Script Output** - Use ASCII status indicators and formatting in all print statements
2. **Configuration Files** - Stick to ASCII characters in JSON, YAML, and other config formats
3. **Documentation** - While Markdown can handle Unicode, prefer ASCII for code blocks and examples
4. **Comments** - Use ASCII characters in code comments to prevent encoding issues
5. **File Names** - Always use ASCII characters in file and directory names

**Testing for Encoding Issues:**
- **Validate all Python scripts** can be loaded and executed without encoding errors
- **Test configuration files** parse correctly on different platforms
- **Check JSON/YAML files** load properly using standard libraries
- **Verify file operations** work correctly across Windows, Linux, and Mac systems

### 11. Operating System Awareness and Command Selection

**Platform Detection Requirements:**
- **ALWAYS detect the current operating system** before suggesting or using shell commands
- **USE platform-appropriate commands** based on the detected environment
- **PROVIDE cross-platform alternatives** when commands differ between operating systems
- **DOCUMENT platform-specific behaviors** and command variations

**Operating System Command Standards:**

**Windows (PowerShell/Command Prompt):**
```powershell
# File operations
Get-ChildItem                    # List files (not ls)
Move-Item src dest              # Move files (not mv)
Copy-Item src dest              # Copy files (not cp)
Remove-Item file                # Delete files (not rm)
Test-Path file                  # Check if file exists (not [ -f ])
New-Item -ItemType Directory    # Create directory (not mkdir)

# Process management
Get-Process                     # List processes (not ps)
Stop-Process -Name name         # Kill process (not kill)

# Network
Test-NetConnection host -Port port  # Test connection (not nc/telnet)
```

**Linux/Mac (Bash/Zsh):**
```bash
# File operations
ls                              # List files
mv src dest                     # Move files
cp src dest                     # Copy files
rm file                         # Delete files
[ -f file ]                     # Check if file exists
mkdir -p dir                    # Create directory

# Process management
ps aux                          # List processes
kill -9 pid                     # Kill process

# Network
nc -zv host port               # Test connection
```

**Cross-Platform Python Alternatives:**
```python
import os
import platform
import shutil
from pathlib import Path

# Detect OS
current_os = platform.system()  # Returns: 'Windows', 'Linux', 'Darwin'

# Cross-platform file operations
Path('file').exists()           # Check file existence
shutil.move(src, dest)          # Move files
shutil.copy2(src, dest)         # Copy files
os.makedirs(path, exist_ok=True)  # Create directories
```

**Implementation Guidelines:**
1. **Detect Environment** - Check platform.system() or use context clues from terminal output
2. **Use Appropriate Commands** - Select Windows PowerShell commands for Windows, bash commands for Linux/Mac
3. **Provide Alternatives** - When documenting, show both Windows and Unix variations
4. **Test Commands** - Verify commands work on the target platform before suggesting them
5. **Default Assumptions** - When uncertain, ask for clarification or provide both options

**Current Project Context Detection:**
- **Terminal Type** - PowerShell indicates Windows environment
- **Path Separators** - Backslashes (\) indicate Windows, forward slashes (/) indicate Unix
- **File Extensions** - .exe files suggest Windows environment
- **Environment Variables** - %VAR% (Windows) vs $VAR (Unix)

**Command Selection Priority:**
1. **Use detected OS commands** - Primary choice based on environment detection
2. **Provide cross-platform Python** - When shell commands vary significantly
3. **Document both variants** - In documentation, show Windows and Unix examples
4. **Test on target platform** - Always validate commands work in the current environment

### 12. Repository Resilience and Clean Operation Standards

**Git Clean Compatibility Requirements:**
- **ALL essential files** must be committed to the repository and not rely on generated or cached content
- **ENSURE seamless operation** after `git clean -xdf` command removes all untracked and ignored files
- **TEST repository resilience** by regularly running `git clean -xdf` and verifying all functionality works
- **SEPARATE essential files** from generated content through proper `.gitignore` configuration

**Essential Files That Must Be Committed:**
1. **Source Code** - All Python scripts, configuration files, and application code
2. **Documentation** - All markdown files, guides, and instructional content
3. **Configuration Templates** - `.env.example`, config templates, and setup files
4. **Project Structure** - Directory placeholder files (`.gitkeep`) to maintain folder structure
5. **Build Scripts** - Setup scripts, deployment configurations, and automation tools
6. **Development Tools** - VS Code settings, tasks, linting configurations, and development aids

**Generated/Cached Content (Should NOT be committed):**
1. **Virtual Environments** - `.venv/`, `venv/`, `env/` directories
2. **Downloaded Models** - Large model files, cached data, and external dependencies
3. **Runtime Data** - Logs, temporary files, cache directories, and session data
4. **User-Specific Files** - Local configuration overrides and personal settings
5. **Build Artifacts** - Compiled code, distribution packages, and generated documentation
6. **External Dependencies** - `node_modules/`, Python package caches, and downloaded libraries

**Repository Resilience Testing:**
```powershell
# Windows PowerShell - Test repository resilience
git clean -xdf                           # Remove all untracked and ignored files
python scripts/setup/validate-setup.py   # Verify core functionality works
python scripts/initialize.py            # Test complete setup process
```

**Implementation Standards:**
1. **Directory Structure Preservation** - Use `.gitkeep` files to maintain empty directories
2. **Configuration Templates** - Provide example configurations without sensitive data
3. **Setup Automation** - Ensure initialization scripts recreate necessary runtime directories
4. **Dependency Management** - Use `requirements.txt` and package managers for reproducible environments
5. **Documentation Completeness** - Include all setup instructions for clean repository initialization

**Clean Operation Verification:**
- **After `git clean -xdf`** - All essential functionality should remain intact
- **Setup Scripts Work** - Initialization and setup scripts should run without errors
- **Documentation Available** - All guides and instructions should be accessible
- **Configuration Valid** - Template files should provide clear setup guidance
- **Development Tools** - VS Code workspace should function with all tasks and settings

**Recovery Process After Git Clean:**
1. **Python Environment** - Automatically recreated by `configure_python_environment` tool
2. **Dependencies** - Reinstalled via `requirements.txt` and setup scripts
3. **Runtime Directories** - Recreated by initialization scripts (`models/`, `data/`, etc.)
4. **Downloaded Content** - Re-downloaded as needed by model management scripts
5. **Cache Files** - Regenerated during normal operation

## Enforcement

These guidelines are **mandatory** for all development work on this project. Any LLM working on this project must:

1. **Reference these guidelines** before creating or modifying any files
2. **Follow the directory structure** requirements without exception
3. **Update navigation** in parent README files when adding new documentation
4. **Maintain consistency** with established patterns and conventions
5. **Validate all implementations** through testing before marking tasks complete
6. **Verify code functionality** by running scripts and commands when possible
7. **Test configuration files** for proper syntax and loading behavior
8. **Document testing results** and any platform-specific findings
9. **Leverage the memory bank** for project context, patterns, and user preferences
10. **Update memory bank** with new learnings and project evolution insights
11. **Maintain session continuity** by building on stored knowledge and decisions
12. **Identify and ignore output files** that should not be tracked in Git
13. **Update .gitignore** immediately when new file patterns need to be excluded
14. **Maintain repository cleanliness** by preventing unwanted files from being committed
15. **NEVER commit sensitive information** including API keys, passwords, tokens, or PII to GitHub
16. **Scan all content** for sensitive data patterns before any commit or file creation
17. **Use secure configuration patterns** with environment variables and template files
18. **Implement data classification standards** to protect sensitive information at all levels
19. **Follow security remediation protocols** if sensitive data is accidentally exposed
20. **ALWAYS use ASCII characters** in code, configuration files, and structured data to prevent encoding issues
21. **Test all files for encoding compatibility** across different platforms and ensure universal accessibility
22. **DETECT the current operating system** and use appropriate platform-specific commands
23. **Use Windows PowerShell commands** when working in Windows environments, Linux/Mac bash commands otherwise
24. **ENSURE repository resilience** by committing all essential files and testing `git clean -xdf` compatibility
25. **SEPARATE essential files** from generated content and verify seamless operation after clean operations
26. **UPDATE task status accurately** in tasks/tasks-prd.md immediately after completing any work items or subtasks
27. **MAINTAIN task completion tracking** to ensure documented progress matches actual implementation status
28. **IMPLEMENT comprehensive Docker monitoring** for all platform containers with health checks, alerting, and automated recovery
29. **DETECT container failures immediately** and implement proper monitoring to prevent unnoticed service degradation
30. **RESPOND to 'push' command** by analyzing staged changes, generating descriptive commit messages, and executing git commit/push sequence

## Updates to Guidelines

When project needs require changes to these guidelines:
1. Update this `guidelines.prompt.md` file with new requirements
2. Update any affected documentation to match new guidelines
3. Ensure all team members/LLMs reference the updated guidelines

---

**Remember**: Good documentation organization is crucial for project maintainability and contributor onboarding. These guidelines ensure every piece of documentation has a logical place and clear navigation path.
```

Sunday, September 21, 2025 5:44:56 PM



