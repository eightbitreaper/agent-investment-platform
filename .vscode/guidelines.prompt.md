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
- Use consistent link formatting: `[Clear Description](path/to/file.md)`

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
- [Section 1](#section-1)
- [Section 2](#section-2)

## Section Content
[Organized, scannable content with proper formatting]

## Related Documentation
- [Related Guide](../path/to/related.md)
- [Parent Section](README.md)
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

## Updates to Guidelines

When project needs require changes to these guidelines:
1. Update this `guidelines.prompt.md` file with new requirements
2. Update any affected documentation to match new guidelines
3. Ensure all team members/LLMs reference the updated guidelines

---

**Remember**: Good documentation organization is crucial for project maintainability and contributor onboarding. These guidelines ensure every piece of documentation has a logical place and clear navigation path.
```
