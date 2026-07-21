# Skillian Architecture Implementation Guides

This directory contains step-by-step guides for implementing the proposed architectural improvements from [AGENT_ARCHITECTURE_PROPOSALS.md](../AGENT_ARCHITECTURE_PROPOSALS.md).

## Overview

These guides transform Skillian from a Python-only skill system to a hybrid config-based architecture that enables:

- **No-code skill definitions** via SKILL.md and tools.yaml
- **Dynamic skill loading** with auto-discovery
- **Hot-reload** during development
- **OpenAPI integration** for automatic tool generation
- **CLI management** for non-developers

## Implementation Order

Follow these guides in sequence:

| # | Guide | Description | Priority |
|---|-------|-------------|----------|
| 1 | [Dynamic Skill Loader](01_DYNAMIC_SKILL_LOADER.md) | Auto-discover and load skills from directories | High |
| 2 | [SKILL.md Parser](02_SKILL_MD_PARSER.md) | Parse skill definitions from markdown files | High |
| 3 | [YAML Tool Definitions](03_YAML_TOOL_DEFINITIONS.md) | Load tools from YAML configuration | High |
| 4 | [Skill CLI](04_SKILL_CLI.md) | Command-line skill management | Medium |
| 5 | [OpenAPI Tool Generator](05_OPENAPI_TOOL_GENERATOR.md) | Generate tools from API specs | Medium |
| 6 | [Query Templates](06_QUERY_TEMPLATES.md) | Zero-code database query tools | Medium |
| 7 | [Skill Migration](07_SKILL_MIGRATION.md) | Migrate existing Python skills | Medium |

## Quick Start

### Phase 1: Foundation (Guides 1-3)

These guides establish the core infrastructure:

```bash
# After implementing guides 1-3, you can:

# Create a new skill directory
mkdir -p app/skills/inventory

# Add SKILL.md
cat > app/skills/inventory/SKILL.md << 'EOF'
---
name: inventory
description: Inventory diagnostics skill
version: "1.0.0"
connector: datasphere
---

# Inventory Skill

## Instructions
Help users diagnose inventory issues...
EOF

# Add tools.yaml
cat > app/skills/inventory/tools.yaml << 'EOF'
tools:
  - name: check_stock
    description: Check stock levels
    parameters:
      - name: material
        type: string
        required: true
    query_template: |
      SELECT material, quantity FROM STOCK
      WHERE material = '{material}'
EOF

# Skill auto-loads on server start!
```

### Phase 2: Tooling (Guides 4-6)

Add developer experience improvements:

```bash
# After implementing guides 4-6, you can:

# List all skills
uv run skillian skill list

# Validate a skill
uv run skillian skill validate inventory

# Generate tools from OpenAPI
uv run skillian openapi generate specs/api.yaml --skill datasphere

# Hot-reload during development
uv run skillian skill reload inventory
```

### Phase 3: Migration (Guide 7)

Convert existing Python skills:

```bash
# Migrate existing skill
uv run skillian skill migrate financial --dry-run

# Review and apply
uv run skillian skill migrate financial --no-dry-run
```

## Architecture Overview

### Before (Python-only)

```
app/skills/financial/
├── skill.py          # Python class with metadata, prompts, tool registration
├── tools.py          # Pydantic schemas + implementations
└── knowledge/        # RAG documents
```

**Adding a tool requires:**
1. Define Pydantic input schema in tools.py
2. Implement function in tools.py
3. Register Tool in skill.py
4. Restart server

### After (Hybrid)

```
app/skills/financial/
├── SKILL.md          # Metadata + instructions (YAML frontmatter + Markdown)
├── tools.yaml        # Tool definitions (parameters, descriptions)
├── tools.py          # Just implementations (no schemas)
└── knowledge/        # RAG documents
```

**Adding a tool requires:**
1. Add entry to tools.yaml
2. Implement function in tools.py
3. Run `skillian skill reload financial` (or auto-reload in dev)

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Skill CLI                                 │
│  skillian skill [list|create|validate|reload|test]              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      Skill Loader                                │
│  - Discovers skills from app/skills/                            │
│  - Loads SKILL.md (parser) + tools.yaml (yaml loader)           │
│  - Supports hot-reload                                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  SKILL.md       │  │  tools.yaml     │  │  tools.py       │
│  Parser         │  │  Loader         │  │  Implementations│
│                 │  │                 │  │                 │
│  - Frontmatter  │  │  - Parameters   │  │  - Functions    │
│  - Instructions │  │  - Descriptions │  │  - Async        │
│  - Examples     │  │  - Templates    │  │  - Connector    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ ConfiguredSkill │
                    │ or PythonSkill  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  SkillRegistry  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Agent       │
                    └─────────────────┘
```

## Files to Create

After completing all guides, you'll have these new files:

```
app/
├── cli/
│   ├── __init__.py              # Main CLI app
│   ├── skill_commands.py        # skill subcommands
│   └── openapi_commands.py      # openapi subcommands
├── core/
│   ├── exceptions.py            # Custom exceptions
│   ├── configured_skill.py      # Config-based skill class
│   ├── skill_loader.py          # Dynamic loader
│   ├── skill_parser.py          # SKILL.md parser
│   ├── skill_validator.py       # Validation utilities
│   ├── yaml_tools.py            # YAML tool loader
│   ├── query_template.py        # Query template engine
│   └── openapi_loader.py        # OpenAPI generator
└── skills/
    └── _templates/
        └── basic/
            ├── SKILL.md
            ├── tools.yaml
            └── tools.py
```

## Dependencies to Add

```bash
uv add typer[all] python-frontmatter pyyaml
```

## Testing Strategy

Each guide includes tests. Run all tests:

```bash
# Run all new tests
uv run pytest tests/test_skill_loader.py tests/test_skill_parser.py tests/test_yaml_tools.py tests/test_query_template.py tests/test_openapi_loader.py tests/test_cli.py -v

# Run with coverage
uv run pytest --cov=app.core --cov=app.cli tests/
```

## Compatibility

The new system maintains full backward compatibility:

- **Existing Python skills** continue to work unchanged
- **New config-based skills** work alongside Python skills
- **Gradual migration** is supported (migrate one skill at a time)
- **Mixed mode** is fully supported

## Next Steps After Implementation

1. **Migrate existing skills** using Guide 7
2. **Create skill templates** for your organization's patterns
3. **Add OpenAPI specs** for your SAP APIs
4. **Document skill standards** for your team
5. **Consider multi-agent** architecture for complex scenarios (future)

## References

- [AGENT_ARCHITECTURE_PROPOSALS.md](../AGENT_ARCHITECTURE_PROPOSALS.md) - Original research and proposals
- [Agent Skills Specification](https://agentskills.io/specification) - Industry standard for SKILL.md
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/) - Tool integration patterns
