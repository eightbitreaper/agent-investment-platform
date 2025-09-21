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

## Updates to Guidelines

When project needs require changes to these guidelines:
1. Update this `guidelines.prompt.md` file with new requirements
2. Update any affected documentation to match new guidelines  
3. Ensure all team members/LLMs reference the updated guidelines

---

**Remember**: Good documentation organization is crucial for project maintainability and contributor onboarding. These guidelines ensure every piece of documentation has a logical place and clear navigation path.
```