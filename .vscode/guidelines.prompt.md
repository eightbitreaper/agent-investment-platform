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

## Enforcement

These guidelines are **mandatory** for all development work on this project. Any LLM working on documentation tasks must:

1. **Reference these guidelines** before creating or modifying any markdown files
2. **Follow the directory structure** requirements without exception
3. **Update navigation** in parent README files when adding new documentation
4. **Maintain consistency** with established patterns and conventions

## Updates to Guidelines

When project needs require changes to these guidelines:
1. Update this `guidelines.prompt.md` file with new requirements
2. Update any affected documentation to match new guidelines  
3. Ensure all team members/LLMs reference the updated guidelines

---

**Remember**: Good documentation organization is crucial for project maintainability and contributor onboarding. These guidelines ensure every piece of documentation has a logical place and clear navigation path.
```