/**
 * Migration report CLI:
 *
 *   npm run report -- [--workspace <name>] [--skip-llm]
 *
 * Thin wrapper around lib/report/job.ts. Fails the process when any
 * displayed Tier-1 finding does not re-validate on its cited evidence.
 */
import { closePool, query } from "../lib/db/client";
import { runReport } from "../lib/report/job";

function arg(name: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

async function main() {
  const only = arg("workspace");
  const skipLlm = process.argv.includes("--skip-llm");
  const workspaces = only
    ? [only]
    : (await query<{ name: string }>(`select name from workspaces order by name`)).map((w) => w.name);

  for (const w of workspaces) {
    console.log(`\n=== ${w} ===`);
    const r = await runReport(w, { skipLlm });
    console.log(
      `run ${r.runId}: ${r.tier1} tier-1, ${r.tier2} tier-2, ${r.tier3} tier-3 displayed; ` +
        `${r.suppressed} suppressed (debug view only); llm scope ${r.llmScope} objects`
    );
    console.log(`tier-1 spot-check: ${r.spotcheck.reconfirmed}/${r.spotcheck.total} validators re-confirmed on cited evidence`);
    const [headline] = await query(
      `select
         count(*) filter (where tier = 1 and not suppressed) as tier1,
         count(*) filter (where tier = 2 and not suppressed) as tier2,
         count(*) filter (where tier = 3 and not suppressed) as tier3,
         count(*) filter (where suppressed) as suppressed,
         count(distinct object_id) filter (where tier in (1,2) and not suppressed) as affected_objects
       from findings where workspace_id = (select id from workspaces where name = $1)`,
      [w]
    );
    console.log(`headline (SQL): ${JSON.stringify(headline)}`);
    if (r.spotcheck.reconfirmed !== r.spotcheck.total) {
      console.error("GATE FAIL: not every Tier-1 finding re-validates");
      process.exitCode = 1;
    }
  }
  await closePool();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
