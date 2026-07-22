/**
 * Upsert the S/4HANA incompatibility rules from lib/rules/rules.json into the
 * incompatibility_rules table. Idempotent; run any time the file changes.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { closePool, query } from "../lib/db/client";

async function main() {
  const { rules } = JSON.parse(
    readFileSync(join(import.meta.dirname, "..", "lib", "rules", "rules.json"), "utf8")
  );
  for (const r of rules) {
    await query(
      `insert into incompatibility_rules
         (id, title, description, sap_note, simplification_item, source_url, detection, replacement,
          tier1_eligible, source_status, verified_at, severity,
          source_excerpt, excerpt_source_url, remediation_effort, effort_rationale, verified_release)
       values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
       on conflict (id) do update set
         title = excluded.title,
         description = excluded.description,
         sap_note = excluded.sap_note,
         simplification_item = excluded.simplification_item,
         source_url = excluded.source_url,
         detection = excluded.detection,
         replacement = excluded.replacement,
         tier1_eligible = excluded.tier1_eligible,
         source_status = excluded.source_status,
         verified_at = excluded.verified_at,
         severity = excluded.severity,
         source_excerpt = excluded.source_excerpt,
         excerpt_source_url = excluded.excerpt_source_url,
         remediation_effort = excluded.remediation_effort,
         effort_rationale = excluded.effort_rationale,
         verified_release = excluded.verified_release`,
      [
        r.id,
        r.title,
        r.description,
        r.sap_note,
        r.simplification_item ?? null,
        r.source_url ?? null,
        JSON.stringify(r.detection),
        r.replacement ?? null,
        r.tier1_eligible,
        // A6: reports render a note number only when the rule's source was
        // explicitly web-verified; the verification pass records these fields
        // in rules.json — absent fields mean unverified.
        r.source_status === "verified" ? "verified" : "unverified",
        r.verified_at ?? null,
        // grade reference data: 'high' = construct removed outright in
        // S/4HANA, 'medium' = replaced data model with compatibility views
        r.severity ?? "medium",
        // CO-07 source layer: verbatim quote from the public source (curated,
        // human-approved), deterministic effort band + rationale, and the
        // S/4HANA release documentation set the rule was checked against
        r.source_excerpt ?? null,
        r.excerpt_source_url ?? null,
        r.remediation_effort ?? null,
        r.effort_rationale ?? null,
        r.verified_release ?? null,
      ]
    );
  }
  const [row] = await query<{ n: string }>(`select count(*) as n from incompatibility_rules`);
  console.log(`rules upserted: ${rules.length} (table now has ${row.n})`);
  await closePool();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
