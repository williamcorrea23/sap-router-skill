/**
 * Minimal SQL migration runner.
 *
 * Applies lib/db/migrations/*.sql in filename order, tracking applied files in
 * schema_migrations. Each migration runs in its own transaction.
 *
 * Usage:
 *   npm run migrate            # apply pending migrations
 *   npm run migrate -- --status  # list applied/pending, change nothing
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { Client } from "pg";

const MIGRATIONS_DIR = join(import.meta.dirname, "..", "lib", "db", "migrations");

async function main() {
  const statusOnly = process.argv.includes("--status");
  const url = process.env.DATABASE_URL;
  if (!url) {
    console.error("DATABASE_URL is not set (load .env.local)");
    process.exit(1);
  }

  const files = readdirSync(MIGRATIONS_DIR)
    .filter((f) => f.endsWith(".sql"))
    .sort();

  const client = new Client({ connectionString: url });
  await client.connect();
  try {
    await client.query(
      `create table if not exists schema_migrations (
         filename text primary key,
         applied_at timestamptz not null default now()
       )`
    );
    const { rows } = await client.query("select filename from schema_migrations");
    const applied = new Set(rows.map((r) => r.filename));
    const pending = files.filter((f) => !applied.has(f));

    if (statusOnly) {
      for (const f of files) console.log(`${applied.has(f) ? "applied" : "pending"}  ${f}`);
      console.log(`${applied.size} applied, ${pending.length} pending`);
      return;
    }

    for (const f of pending) {
      const sql = readFileSync(join(MIGRATIONS_DIR, f), "utf8");
      await client.query("begin");
      try {
        await client.query(sql);
        await client.query("insert into schema_migrations (filename) values ($1)", [f]);
        await client.query("commit");
        console.log(`applied  ${f}`);
      } catch (e) {
        await client.query("rollback");
        console.error(`FAILED  ${f}: ${(e as Error).message}`);
        process.exit(1);
      }
    }
    console.log(pending.length ? `done (${pending.length} applied)` : "up to date");
  } finally {
    await client.end();
  }
}

main();
