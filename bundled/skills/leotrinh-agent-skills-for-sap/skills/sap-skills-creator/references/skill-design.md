# Skill Design

Load this file during the Design phase. Use the coherent-unit framework
below to shape the resulting `SKILL.md` before writing it.

## The Coherent-Unit Test

A skill should behave like a well-designed function:

- **One responsibility.** If two responsibilities appear, split the skill.
- **Named inputs.** The user or agent knows what to supply.
- **Named outputs.** The consumer knows what to expect.
- **Clear activation.** A short description explains when to fire.
- **Composability.** The skill cooperates with other skills instead of
  duplicating them.
- **No hidden state.** The skill does not depend on facts that the user
  cannot see.

Reject a design when any test above fails.

## Choosing Operating Modes

Most SAP skills have more than one execution path. Prefer explicit modes
to implicit branching inside prose. Common mode shapes:

| Mode | Purpose |
|------|---------|
| **Inspect / read-only** | Discover state before any change. |
| **Preview / dry-run** | Describe the intended change without executing. |
| **Execute** | Perform the change with human authorization. |
| **Rollback / undo** | Reverse the change when possible. |
| **Report** | Emit a structured result artefact. |

Document the mode in a table at the top of `SKILL.md` and reference it in
each phase of the workflow.

## Procedures Instead of Declarations

Replace vague declarations with sequences.

Bad:

```text
Follow SAP best practices.
Handle errors appropriately.
Use secure authentication.
```

Good:

```text
Inspect the project's existing destination model before adding
credentials.
Use the repository's secure environment-variable pattern.
Stop when required values are missing.
Never write credentials into generated commands or documentation.
```

A procedure has:

- A trigger.
- A short ordered list of steps.
- A verifiable output.
- A stop condition when a step cannot complete.

Every meaningful workflow in `SKILL.md` should be a procedure of this
shape.

## Defaults vs Menus

Give the agent one default path per decision. Reserve menus for cases
where the user must choose (destination selection, transport selection,
language). Long lists of "you could also do X, Y, Z" hurt trigger
precision and inflate the file.

Good default pattern:

```text
Default:
  Use --dest <SID>_<CLIENT>_<USER>_<LANG> resolution.

Deviate only when:
  - The user provides an explicit --url and --user.
  - The user is testing a non-standard tenant.
```

## Decision Trees

Complex workflows benefit from a short decision tree. Keep it flat.

```text
Task: create and activate an ABAP CDS view.

Is a matching MCP tool available?
├── Yes → Use the MCP tool and stop.
└── No  → Continue with this skill.

Is the target package tracked in a transport?
├── Yes → Reuse the existing transport.
└── No  → Ask the user for a transport number or offer to create one.

Was the CDS view created successfully?
├── Yes → Activate it and report the object URL.
└── No  → Stop and report the ADT error verbatim.
```

Do not nest decision trees more than three levels. Move deeper detail to
a reference file.

## Output Contracts

Every skill must state exactly what the agent will report at each end
state.

- **Success**: files changed, remote calls made, transport numbers, next
  suggested step.
- **Partial success**: what worked, what did not, and how to resume.
- **Blocked**: the reason, the missing input, and the exact remediation
  command.
- **Failure**: the tool response verbatim, the interpretation, and the
  suggested next step.

Report contents should be usable without opening the AI transcript.

## Stop Conditions

List concrete triggers that pause the workflow and ask the user for a
decision. Common stop conditions in SAP workflows:

- The target system is production and the user has not confirmed the
  intent.
- Required environment variables are missing.
- The MCP tool that should own this operation is available and works.
- The requested destructive operation is not explicitly authorized in the
  current exchange.
- Sources conflict (for example, different SAP releases have different
  behaviour).
- The validator returns `FAIL` on the generated skill.

Stops must be honest: never silently retry, and never claim success when
the tool response does not confirm it.

## Compatibility Boundaries

Skills should not silently break each other. Document:

- Which other skills this one depends on, if any.
- Which environment variables or files it expects to already exist.
- Which SAP release ranges it has been designed for.
- Whether it competes with, replaces, or complements an MCP tool.

Prefer `compatibility` frontmatter for machine-readable statements. Keep
long human-readable explanations in `README.md`.

## Internal vs Public Skills

Internal team skills may reference internal systems, project-specific
naming conventions, and team runbooks, provided they contain no secrets.

Public skills must:

- Use portable placeholders (`<sid>`, `<user>`, `<transport>`) instead of
  real values.
- Reference public SAP documentation instead of internal wikis.
- Include a clear disclaimer of non-affiliation with SAP.
- Ship inspectable source only. No prebuilt executables.
- Follow the repository's license, security, and contribution policies.

Ask the user which category applies before writing the skill. Do not
promote an internal skill to public without an explicit sanitization pass.

## Sizing Guidelines

- `SKILL.md`: target 300–450 lines, hard limit 500 lines.
- Reference files: 100–300 lines each. Split when a file grows past 400.
- `README.md`: written for humans, aim for 150–250 lines.
- Templates in `assets/`: fit on one screen when possible.
- Scripts: keep the CLI surface small; hide the details behind flags
  and reference documentation.

If a section grows past its sensible size, extract it into a new
reference file and add a link.

## Common Design Mistakes

- Restating the description in three different places.
- Long command catalogues at the top of `SKILL.md` instead of in a
  reference file.
- Deeply nested reference chains (`SKILL.md → a.md → b.md → c.md`).
- Reference files whose only content is more links.
- Duplicated safety rules between references and `SKILL.md` without a
  single source of truth.
- Inventing SAP endpoints, authorization objects, or product features that
  the design has not verified.
- Producing a script when a short procedure would do the job.

Fix these during design instead of during review.
