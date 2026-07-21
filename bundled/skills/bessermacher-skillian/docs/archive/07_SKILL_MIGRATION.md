# Guide 7: Skill Migration

This guide explains how to migrate existing Python-based skills to the new config-based format (SKILL.md + tools.yaml).

## Overview

Migration converts skills from:

```
skill/
├── skill.py      # Python class with all definitions
└── tools.py      # Tool implementations
```

To:

```
skill/
├── SKILL.md      # Metadata and instructions
├── tools.yaml    # Tool definitions
├── tools.py      # Tool implementations (simplified)
└── knowledge/    # RAG documents
```

## Benefits of Migration

| Aspect | Python-Based | Config-Based |
|--------|--------------|--------------|
| Adding tools | Edit Python code | Edit YAML |
| Changing prompts | Edit Python code | Edit Markdown |
| Hot-reload | Restart required | Supported |
| Non-developer edits | Difficult | Easy |
| Validation | Runtime errors | Schema validation |
| Documentation | Separate files | Self-contained |

## Step-by-Step Migration

### Step 1: Analyze Existing Skill

First, examine the current skill structure:

```python
# app/skills/financial/skill.py (BEFORE)
class FinancialSkill:
    def __init__(self, connector: DatasphereConnector):
        self._connector = connector
        self._tool_impl = FinancialTools(connector)
        self._tools = self._build_tools()

    @property
    def name(self) -> str:
        return "financial"

    @property
    def description(self) -> str:
        return "Diagnose SAP BW financial data issues..."

    @property
    def tools(self) -> list[Tool]:
        return self._tools

    @property
    def system_prompt(self) -> str:
        return """You are a financial data expert..."""

    @property
    def knowledge_paths(self) -> list[str]:
        return [str(Path(__file__).parent / "knowledge")]

    def _build_tools(self) -> list[Tool]:
        return [
            Tool(
                name="check_gl_balance",
                description="Check GL account balance for a period",
                function=self._tool_impl.check_gl_balance,
                input_schema=CheckGLBalanceInput,
            ),
            # ... more tools
        ]
```

### Step 2: Create SKILL.md

Extract metadata and prompts into SKILL.md:

```yaml
# app/skills/financial/SKILL.md (AFTER)
---
name: financial
description: |
  Diagnose SAP BW financial data issues including GL discrepancies,
  cost center allocations, and posting period validations.
  Use when users ask about financial reports or data quality.
version: "1.0.0"
author: skillian
domain: financial
tags: [sap, bw, finance, gl, cost-center]
connector: datasphere
---

# Financial Diagnostics Skill

## Capabilities

- Validate GL account balances across periods
- Check posting period consistency
- Detect missing cost allocations
- Compare actuals vs. budget
- Identify currency conversion issues

## When to Use

Activate this skill when the user asks about:

- GL account discrepancies
- Cost center data issues
- Financial report validation
- Period-end reconciliation

## Instructions

You are a financial data expert specializing in SAP BW diagnostics.

When helping users:

1. Always start by understanding the scope (company code, fiscal year, period)
2. Use `check_gl_balance` for single account validation
3. Use `compare_periods` for trend analysis
4. Present differences with both absolute and percentage values
5. Suggest root causes based on common patterns

### Common Issues to Check

- Currency conversion differences
- Period assignment errors
- Missing reversals
- Intercompany mismatches

## Examples

### Example 1: Balance Check

User: "Check GL account 400000 for company 1000 in 2024"
Assistant: Uses check_gl_balance tool with account=400000, company=1000, year=2024

### Example 2: Period Comparison

User: "Compare Q1 vs Q2 revenue for account 800000"
Assistant: Uses compare_periods tool to analyze the difference between quarters
```

### Step 3: Create tools.yaml

Convert tool definitions from Python to YAML:

```yaml
# app/skills/financial/tools.yaml (AFTER)
tools:
  - name: check_gl_balance
    description: |
      Check GL account balance for a specific period.
      Returns balance details including debit, credit, and net amounts.
      Use this for validating individual account balances.
    parameters:
      - name: account_number
        type: string
        required: true
        description: GL account number (e.g., "400000")
      - name: company_code
        type: string
        required: true
        description: SAP company code (e.g., "1000")
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year (e.g., 2024)
      - name: period
        type: string
        required: false
        description: Specific period (e.g., "001"). Returns full year if not specified.
    implementation: app.skills.financial.tools:check_gl_balance

  - name: compare_periods
    description: |
      Compare account balance between two periods.
      Shows absolute and percentage differences.
      Useful for trend analysis and variance investigation.
    parameters:
      - name: account_number
        type: string
        required: true
        description: GL account to compare
      - name: company_code
        type: string
        required: true
        description: Company code
      - name: period_a
        type: object
        required: true
        description: First period
        properties:
          year:
            type: integer
          period:
            type: string
      - name: period_b
        type: object
        required: true
        description: Second period
        properties:
          year:
            type: integer
          period:
            type: string
    implementation: app.skills.financial.tools:compare_periods

  - name: validate_cost_allocations
    description: Check for missing cost center allocations
    parameters:
      - name: cost_center
        type: string
        required: false
        description: Specific cost center or all if not specified
      - name: fiscal_year
        type: integer
        required: true
        description: Fiscal year
    implementation: app.skills.financial.tools:validate_cost_allocations
```

### Step 4: Simplify tools.py

Remove schema definitions (now in YAML) and keep only implementations:

```python
# app/skills/financial/tools.py (AFTER - simplified)
"""Tool implementations for financial skill."""

from typing import Any


async def check_gl_balance(
    account_number: str,
    company_code: str,
    fiscal_year: int,
    period: str | None = None,
    connector: Any = None,
) -> dict[str, Any]:
    """Check GL account balance.

    Note: Parameters are validated by YAML-generated schema.
    Connector is injected by the skill loader.
    """
    if connector is None:
        return {"error": "No database connection"}

    query = f"""
        SELECT account_number, period,
               SUM(debit) as debit, SUM(credit) as credit
        FROM GL_BALANCES
        WHERE account_number = '{account_number}'
          AND company_code = '{company_code}'
          AND fiscal_year = {fiscal_year}
    """

    if period:
        query += f" AND period = '{period}'"

    query += " GROUP BY account_number, period ORDER BY period"

    results = await connector.execute_sql(query)

    return {
        "account": account_number,
        "company": company_code,
        "fiscal_year": fiscal_year,
        "balances": results,
    }


async def compare_periods(
    account_number: str,
    company_code: str,
    period_a: dict[str, Any],
    period_b: dict[str, Any],
    connector: Any = None,
) -> dict[str, Any]:
    """Compare account balance between two periods."""
    if connector is None:
        return {"error": "No database connection"}

    # Get balance for period A
    balance_a = await check_gl_balance(
        account_number=account_number,
        company_code=company_code,
        fiscal_year=period_a["year"],
        period=period_a.get("period"),
        connector=connector,
    )

    # Get balance for period B
    balance_b = await check_gl_balance(
        account_number=account_number,
        company_code=company_code,
        fiscal_year=period_b["year"],
        period=period_b.get("period"),
        connector=connector,
    )

    # Calculate differences
    total_a = sum(b.get("debit", 0) - b.get("credit", 0) for b in balance_a.get("balances", []))
    total_b = sum(b.get("debit", 0) - b.get("credit", 0) for b in balance_b.get("balances", []))

    diff = total_b - total_a
    pct = (diff / total_a * 100) if total_a else 0

    return {
        "account": account_number,
        "period_a": period_a,
        "period_b": period_b,
        "balance_a": total_a,
        "balance_b": total_b,
        "difference": diff,
        "difference_pct": round(pct, 2),
    }


async def validate_cost_allocations(
    fiscal_year: int,
    cost_center: str | None = None,
    connector: Any = None,
) -> dict[str, Any]:
    """Check for missing cost center allocations."""
    if connector is None:
        return {"error": "No database connection"}

    query = """
        SELECT document_number, posting_date, amount
        FROM FI_DOCUMENTS
        WHERE fiscal_year = {fiscal_year}
          AND cost_center IS NULL
          AND gl_account LIKE '6%'
    """

    if cost_center:
        query = query.replace(
            "cost_center IS NULL",
            f"cost_center = '{cost_center}'"
        )

    results = await connector.execute_sql(query.format(fiscal_year=fiscal_year))

    return {
        "fiscal_year": fiscal_year,
        "cost_center": cost_center or "all",
        "missing_allocations": len(results),
        "documents": results[:50],  # Limit to first 50
    }
```

### Step 5: Delete skill.py (Optional)

Once migrated, you can delete the Python skill class:

```bash
rm app/skills/financial/skill.py
```

Or keep it for backward compatibility during transition.

### Step 6: Validate Migration

```bash
# Validate the migrated skill
uv run skillian skill validate financial

# List tools to verify
uv run skillian skill tools financial

# Test a tool
uv run skillian skill test financial
```

## Migration CLI Helper

Add a migration command to automate parts of the process:

```python
# app/cli/skill_commands.py

@skill_app.command("migrate")
def migrate_skill(
    skill_name: str = typer.Argument(..., help="Skill to migrate"),
    dry_run: bool = typer.Option(True, "--dry-run", help="Preview without writing"),
):
    """Migrate a Python-based skill to config-based format."""
    from app.core.skill_loader import SkillLoader

    skill_dir = Path("app/skills") / skill_name

    if not skill_dir.exists():
        console.print(f"[red]Skill not found: {skill_dir}[/red]")
        raise typer.Exit(1)

    skill_py = skill_dir / "skill.py"
    if not skill_py.exists():
        console.print(f"[yellow]No skill.py found - already migrated?[/yellow]")
        raise typer.Exit(0)

    # Check if already has SKILL.md
    if (skill_dir / "SKILL.md").exists():
        console.print(f"[yellow]SKILL.md already exists[/yellow]")
        if not typer.confirm("Overwrite?"):
            raise typer.Exit(0)

    # Load existing skill to extract info
    loader = SkillLoader(Path("app/skills"))
    try:
        skill = loader.load_skill(skill_name)
    except Exception as e:
        console.print(f"[red]Failed to load skill: {e}[/red]")
        raise typer.Exit(1)

    # Generate SKILL.md content
    skill_md_content = _generate_skill_md(skill)

    # Generate tools.yaml content
    tools_yaml_content = _generate_tools_yaml(skill)

    if dry_run:
        console.print("[bold]Generated SKILL.md:[/bold]")
        console.print(Syntax(skill_md_content, "yaml", theme="monokai"))
        console.print("\n[bold]Generated tools.yaml:[/bold]")
        console.print(Syntax(tools_yaml_content, "yaml", theme="monokai"))
        console.print("\n[yellow]Dry run - no files written[/yellow]")
        console.print("Run with --no-dry-run to write files")
        return

    # Write files
    (skill_dir / "SKILL.md").write_text(skill_md_content)
    (skill_dir / "tools.yaml").write_text(tools_yaml_content)

    console.print(f"[green]Migrated skill '{skill_name}'[/green]")
    console.print("Next steps:")
    console.print("  1. Review and enhance SKILL.md")
    console.print("  2. Verify tools.yaml is correct")
    console.print(f"  3. Delete {skill_py} when ready")
    console.print(f"  4. Run: skillian skill validate {skill_name}")


def _generate_skill_md(skill) -> str:
    """Generate SKILL.md from skill object."""
    version = getattr(skill, "version", "1.0.0")
    author = getattr(skill, "author", "")
    domain = getattr(skill, "domain", skill.name)
    tags = getattr(skill, "tags", [skill.name])
    connector = getattr(skill, "connector_type", None)

    frontmatter = f"""---
name: {skill.name}
description: |
  {skill.description}
version: "{version}"
author: {author}
domain: {domain}
tags: {tags}
"""
    if connector:
        frontmatter += f"connector: {connector}\n"
    frontmatter += "---\n"

    body = f"""
# {skill.name.replace('-', ' ').title()} Skill

## Capabilities

- TODO: List skill capabilities

## When to Use

Activate this skill when the user asks about:

- TODO: List trigger topics

## Instructions

{skill.system_prompt}

## Examples

### Example 1: Basic Usage

User: "TODO: Add example query"
Assistant: TODO: Describe expected response
"""

    return frontmatter + body


def _generate_tools_yaml(skill) -> str:
    """Generate tools.yaml from skill tools."""
    import inspect
    import yaml

    tools_config = {"tools": []}

    for tool in skill.tools:
        tool_config = {
            "name": tool.name,
            "description": tool.description,
            "parameters": [],
        }

        # Extract parameters from input schema
        if tool.input_schema:
            for field_name, field_info in tool.input_schema.model_fields.items():
                param = {
                    "name": field_name,
                    "type": _pydantic_type_to_yaml(field_info.annotation),
                    "required": field_info.is_required(),
                    "description": field_info.description or "",
                }
                tool_config["parameters"].append(param)

        # Try to find implementation path
        if tool.function:
            module = inspect.getmodule(tool.function)
            if module:
                tool_config["implementation"] = f"{module.__name__}:{tool.function.__name__}"
            else:
                tool_config["implementation"] = f"app.skills.{skill.name}.tools:{tool.name}"

        tools_config["tools"].append(tool_config)

    return yaml.dump(tools_config, default_flow_style=False, sort_keys=False)


def _pydantic_type_to_yaml(annotation) -> str:
    """Convert Pydantic field type to YAML type string."""
    import typing

    if annotation is None:
        return "string"

    # Handle Optional types
    origin = typing.get_origin(annotation)
    if origin is typing.Union:
        args = typing.get_args(annotation)
        # Filter out NoneType
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            annotation = non_none[0]

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    return type_map.get(annotation, "string")
```

## Batch Migration

For migrating multiple skills:

```bash
# List all Python-based skills
for skill in app/skills/*/skill.py; do
    name=$(dirname "$skill" | xargs basename)
    echo "Migrating: $name"
    uv run skillian skill migrate "$name" --dry-run
done

# After review, run without dry-run
for skill in app/skills/*/skill.py; do
    name=$(dirname "$skill" | xargs basename)
    uv run skillian skill migrate "$name" --no-dry-run
done
```

## Migration Checklist

For each skill:

- [ ] Run `skillian skill migrate <name> --dry-run`
- [ ] Review generated SKILL.md
- [ ] Enhance instructions and examples
- [ ] Review generated tools.yaml
- [ ] Verify parameter types and descriptions
- [ ] Run `skillian skill validate <name>`
- [ ] Test each tool manually
- [ ] Run `skillian skill test <name>`
- [ ] Delete old skill.py
- [ ] Update any imports that referenced the old class

## Troubleshooting

### Tool not loading after migration

Check that `implementation` path is correct:

```yaml
# Must match actual module path
implementation: app.skills.financial.tools:check_gl_balance
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^
#              Module path                Function name
```

### Connector not injected

Ensure SKILL.md specifies connector:

```yaml
---
connector: datasphere  # This triggers connector injection
---
```

### Schema validation errors

Compare old Pydantic schema with new YAML parameters:

```python
# Old schema
class CheckGLBalanceInput(BaseModel):
    account: str = Field(..., description="Account number")  # required
    period: str | None = Field(None, description="Period")   # optional
```

```yaml
# New YAML - must match
parameters:
  - name: account
    type: string
    required: true           # Matches ...
    description: Account number
  - name: period
    type: string
    required: false          # Matches None default
    description: Period
```

## Summary

Migration involves:

1. **Extract metadata** → SKILL.md frontmatter
2. **Extract instructions** → SKILL.md markdown
3. **Convert tool definitions** → tools.yaml
4. **Simplify implementations** → tools.py (remove schemas)
5. **Delete skill.py** → No longer needed

Benefits:
- Easier maintenance
- Hot-reload support
- Self-documenting skills
- Non-developer friendly
