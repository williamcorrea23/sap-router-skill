/**
 * Operator setup: create a company and its first admin invitation. There is
 * no self-registration — this is how every tenant starts.
 *
 *   npm run create-company -- --name "<company name>" --admin-email admin@example.com
 *
 * Prints the invite link (and tries to send it via Supabase's invite
 * mailer). The invitee opens the link, sets a password, and lands in the
 * app as the company's admin.
 */
import { randomBytes } from "node:crypto";
import { Client } from "pg";
import { createClient } from "@supabase/supabase-js";

function arg(flag: string): string | undefined {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

const INVITE_TTL_DAYS = 7;

async function main() {
  const name = arg("--name");
  const adminEmail = arg("--admin-email")?.trim().toLowerCase();
  if (!name || !adminEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(adminEmail)) {
    console.error('Usage: npm run create-company -- --name "<company name>" --admin-email admin@example.com');
    process.exit(1);
  }
  const dbUrl = process.env.DATABASE_URL;
  if (!dbUrl) {
    console.error("DATABASE_URL is not set (load .env.local)");
    process.exit(1);
  }

  const client = new Client({ connectionString: dbUrl });
  await client.connect();
  try {
    const existing = await client.query(`select id from companies where name = $1`, [name]);
    let companyId: string;
    if (existing.rows.length > 0) {
      companyId = existing.rows[0].id;
      console.log(`Company "${name}" already exists (${companyId}) — creating a new invitation.`);
    } else {
      const res = await client.query(
        `insert into companies (name) values ($1) returning id`,
        [name]
      );
      companyId = res.rows[0].id;
      console.log(`Company "${name}" created (${companyId}).`);
    }

    const member = await client.query(
      `select 1 from profiles p join auth.users u on u.id = p.user_id where lower(u.email) = $1`,
      [adminEmail]
    );
    if (member.rows.length > 0) {
      console.error(`${adminEmail} already has an account — invitations are for new users only.`);
      process.exit(1);
    }

    const token = randomBytes(24).toString("base64url");
    await client.query(
      `insert into invitations (company_id, email, role, token, expires_at)
       values ($1, $2, 'admin', $3, now() + interval '${INVITE_TTL_DAYS} days')`,
      [companyId, adminEmail, token]
    );

    const site = (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
    const inviteUrl = `${site}/invite/${token}`;
    console.log(`\nAdmin invitation for ${adminEmail} (expires in ${INVITE_TTL_DAYS} days):`);
    console.log(`\n  ${inviteUrl}\n`);

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (supabaseUrl && serviceKey) {
      const admin = createClient(supabaseUrl, serviceKey, {
        auth: { autoRefreshToken: false, persistSession: false },
      });
      const { error } = await admin.auth.admin.inviteUserByEmail(adminEmail, {
        redirectTo: inviteUrl,
      });
      console.log(
        error
          ? `Invite email not sent (${error.message}) — share the link above directly.`
          : "Invite email sent via Supabase."
      );
    } else {
      console.log("SUPABASE_SERVICE_ROLE_KEY not set — share the link above directly.");
    }
  } finally {
    await client.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
