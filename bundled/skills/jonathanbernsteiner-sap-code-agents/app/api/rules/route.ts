/**
 * Rule catalog data: GET /api/rules (CO-07).
 * All seeded S/4HANA incompatibility rules with their source layer (SAP Note,
 * verbatim Simplification List excerpt + page link, effort band, detection
 * spec).
 */
import { NextRequest } from "next/server";
import { requireUser } from "../../../lib/auth/server";
import { query } from "../../../lib/db/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const auth = await requireUser(req);
  if (auth instanceof Response) return auth;

  const rules = await query(
    `select r.id, r.title, r.description, r.severity, r.remediation_effort, r.effort_rationale,
            r.replacement, r.detection, r.tier1_eligible, r.verified_release,
            case when r.source_status = 'verified' then r.sap_note else null end as sap_note,
            case when r.source_status = 'verified' then r.simplification_item else null end as simplification_item,
            case when r.source_status = 'verified' then r.source_url else null end as source_url,
            r.source_status,
            r.source_excerpt, r.excerpt_source_url
     from incompatibility_rules r
     order by r.severity desc, r.id`
  );

  return Response.json({ rules });
}
