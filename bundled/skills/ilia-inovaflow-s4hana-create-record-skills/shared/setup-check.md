# Setup check — auto-bootstrap `.env` on first invocation

**Run this check at the very start of every skill invocation, before reading any other instructions or invoking any tool. This is non-negotiable.**

## The rule

The skill MUST get credentials from EXACTLY one of these two sources:

1. A `.env` file in the **user's current working directory** (`pwd`)
2. Environment variables (`SAP_HOST`, `SAP_AUTH_MODE`, etc.) **exported in the shell that launched the agent**

**Do NOT use credentials from any other source.** This includes:

- ❌ Credentials remembered from earlier in this conversation
- ❌ Credentials from a `.env` in a parent directory or a different project
- ❌ Credentials from `~/.env` or `~/.config/sap/.env`
- ❌ Credentials baked into memory files (CLAUDE.md, MEMORY.md, etc.)
- ❌ Credentials inferred from prior runs

If the user previously used a tenant in another conversation, those credentials do NOT carry over. Each project gets its own `.env`. If `.env` isn't in the **current** working directory and the relevant env vars aren't set, the skill MUST create `.env` from the template and wait.

## The check (do these steps in order, every time)

### Step 1 — Announce that you're checking

Tell the user, briefly:

> Checking for SAP credentials in `<current cwd>`...

This signals to the user that you're about to look + makes the boundary clear.

### Step 2 — Test the two valid sources

```bash
# Source A: .env file in CURRENT working directory (not parent, not home)
test -f ./.env

# Source B: shell-exported vars
test -n "$SAP_HOST" && test -n "$SAP_AUTH_MODE"
```

If either passes → use those credentials, skip to the skill's main work. Otherwise, continue.

### Step 3 — Create `.env` template in CWD

The bundled `.env.example` lives in the plugin's installed location. Fetch the canonical version from GitHub raw (always up-to-date):

```bash
curl -fsSL https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example -o ./.env
```

If `curl` fails (offline), fall back to the locally-installed template — search for `.env.example` under `~/.claude/skills/` or `~/<agent>/skills/`.

**NEVER overwrite an existing `.env`.** Check `test ! -f ./.env` before writing.

### Step 4 — Add `.env` to `.gitignore`

```bash
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

Never let secrets leak via git.

### Step 5 — Tell the user clearly and wait

Use this exact tone (warm + directive — not asking permission, just informing):

> ✓ Created `.env` template in `<cwd>` and added it to `.gitignore`. Open the file and fill in:
>
> - **`SAP_HOST`** — your tenant URL (e.g. `https://my<tenant-id>-api.s4hana.cloud.sap`)
> - **`SAP_CLIENT`** — typically `100`
> - **`SAP_AUTH_MODE`** — pick one: `basic` (Cloud Public + comm user), `cc` (on-prem + OAuth client credentials), or `oauth` (Cloud Public + bearer token)
> - Credentials matching your auth mode (the template has inline comments for each block)
>
> Tell me **"ready"** when done and I'll continue with your original task.

Then **stop**. Don't make any API calls. Don't proceed to the skill's Phase 1+. Just wait.

### Step 6 — When user confirms ready, verify

Re-read `./.env`. Check:

1. `SAP_HOST` is set and looks like a real URL (not `<your-...>` placeholder)
2. `SAP_CLIENT` is a number
3. `SAP_AUTH_MODE` is one of `basic` / `cc` / `oauth`
4. Mode-specific credentials are filled in (not placeholders)

If any placeholder remains, point it out specifically and wait again:

> Looks like `SAP_USERNAME` is still `<your-comm-user-name>`. Please replace with your actual user, then say "ready".

Once all required values look real, proceed to the skill's Phase 1.

## When you can skip the check

- Same session, you already passed Phase 0 successfully → cached, no recheck
- User explicitly says: "skip setup, my credentials are in shell" → trust them, proceed
- User says: "use the .env at <specific-path>" → load that file instead (and add the path to .gitignore at that location)

## What to report at the end of Phase 0

After credentials are confirmed, tell the user briefly:

> ✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [original task].

Make the boundary obvious so the user knows credentials are scoped to THIS project.

## Why this is important

Credentials are scoped per-project for safety:

- One project's `.env` should never accidentally hit another tenant
- Conversation memory shouldn't leak credentials across separate work
- Demos, tests, and production should be cleanly isolated

If the user's tenant changed (different demo, different customer, different environment), they should never see "data showed up in the wrong place" because the skill remembered an old credential.
