"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, Copy, Trash2, X } from "lucide-react";
import Card from "../../../../components/ui/Card";
import { inputBaseStyle, primaryButtonStyle } from "../../../../components/ui/formStyles";
import Select from "../../../../components/ui/Select";
import { useProfile } from "../../../../components/useProfile";

interface Member {
  user_id: string;
  display_name: string;
  email: string;
  role: "admin" | "member";
  created_at: string;
}

interface Invitation {
  id: string;
  email: string;
  role: "admin" | "member";
  created_at: string;
  expires_at: string;
}

function RoleBadge({ role }: { role: string }) {
  return (
    <span
      style={{
        fontSize: 10,
        fontWeight: 600,
        color: role === "admin" ? "#CC420B" : "#6E6660",
        backgroundColor: role === "admin" ? "#FCEDE4" : "#F3EFEA",
        border: "1px solid #E8E2DB",
        borderRadius: 5,
        padding: "1px 6px",
      }}
    >
      {role}
    </span>
  );
}

function CopyLink({ url }: { url: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(url).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        });
      }}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        fontSize: 12,
        fontWeight: 600,
        color: copied ? "#CC420B" : "#6E6660",
        background: "none",
        border: "1px solid #E8E2DB",
        borderRadius: 6,
        padding: "4px 10px",
        cursor: "pointer",
        fontFamily: "inherit",
      }}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? "Copied" : "Copy invite link"}
    </button>
  );
}

/** Company settings (admins): members, invitations, removals. */
export default function CompanyPage() {
  const profile = useProfile();
  const [company, setCompany] = useState("");
  const [members, setMembers] = useState<Member[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [forbidden, setForbidden] = useState(false);

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"member" | "admin">("member");
  const [inviteBusy, setInviteBusy] = useState(false);
  const [inviteResult, setInviteResult] = useState<{
    ok: boolean;
    text: string;
    url?: string;
  } | null>(null);
  const [confirmRemove, setConfirmRemove] = useState<string | null>(null);

  const load = useCallback(() => {
    fetch("/api/company")
      .then(async (r) => {
        if (r.status === 403) {
          setForbidden(true);
          return null;
        }
        return r.json();
      })
      .then((d) => {
        if (!d) return;
        setCompany(d.company ?? "");
        setMembers(d.members ?? []);
        setInvitations(d.invitations ?? []);
      })
      .catch(() => {});
  }, []);

  useEffect(load, [load]);

  async function invite(e: React.FormEvent) {
    e.preventDefault();
    setInviteBusy(true);
    setInviteResult(null);
    const res = await fetch("/api/company/invite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
    });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) {
      setInviteResult({ ok: false, text: d.error ?? "Invitation failed." });
    } else {
      setInviteResult({
        ok: true,
        text: d.email_sent
          ? `Invitation email sent to ${d.email}.`
          : `Invitation created for ${d.email} — no email could be sent, share the link below.`,
        url: d.invite_url,
      });
      setInviteEmail("");
      load();
    }
    setInviteBusy(false);
  }

  async function removeMember(userId: string) {
    setConfirmRemove(null);
    await fetch(`/api/company/members/${userId}`, { method: "DELETE" }).catch(() => {});
    load();
  }

  async function revokeInvitation(id: string) {
    await fetch(`/api/company/invitations/${id}`, { method: "DELETE" }).catch(() => {});
    load();
  }

  if (forbidden) {
    return (
      <Card>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Company settings</h2>
        <p style={{ fontSize: 13, color: "#6E6660" }}>
          Only company admins can manage members and invitations.
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>
        Members{company ? ` — ${company}` : ""}
      </h2>
      <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 16 }}>
        Removing a member revokes their access; their past chats stay with the company.
      </p>

      {/* invite first, the member table underneath */}
      <form onSubmit={invite} style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <input
          type="email"
          required
          value={inviteEmail}
          onChange={(e) => setInviteEmail(e.target.value)}
          placeholder="colleague@company.com"
          style={{ ...inputBaseStyle, flex: "0 1 400px", minWidth: 220 }}
        />
        <Select
          ariaLabel="Role"
          value={inviteRole}
          onChange={(v) => setInviteRole(v as "member" | "admin")}
          options={[
            { value: "member", label: "Member" },
            { value: "admin", label: "Admin" },
          ]}
          width={110}
          triggerStyle={{ fontSize: 14, padding: "8px 12px" }}
        />
        <button
          type="submit"
          disabled={inviteBusy || inviteEmail.trim() === ""}
          style={primaryButtonStyle(inviteBusy || inviteEmail.trim() === "")}
        >
          {inviteBusy ? "Inviting…" : "Invite"}
        </button>
      </form>
      {inviteResult && (
        <div
          style={{
            fontSize: 13,
            color: inviteResult.ok ? "#1B1817" : "#CC420B",
            backgroundColor: inviteResult.ok ? "#F3EFEA" : "#FCEDE4",
            borderRadius: 8,
            padding: "10px 12px",
            marginBottom: 12,
            display: "flex",
            flexDirection: "column",
            gap: 8,
            alignItems: "flex-start",
          }}
        >
          {inviteResult.text}
          {inviteResult.url && <CopyLink url={inviteResult.url} />}
        </div>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 6 }}>
        <thead>
          <tr>
            {["Name", "Email", "Role", "Joined", ""].map((h, i) => (
              <th key={i} style={thStyle}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {members.map((m) => {
            const isSelf = m.email.toLowerCase() === profile.email.toLowerCase();
            return (
              <tr key={m.user_id}>
                <td style={{ ...tdStyle, fontWeight: 600, color: "#1B1817" }}>
                  {m.display_name || m.email.split("@")[0]}
                  {isSelf && <span style={{ fontWeight: 400, color: "#A49C95" }}> (you)</span>}
                </td>
                <td style={tdStyle}>{m.email}</td>
                <td style={tdStyle}>
                  <RoleBadge role={m.role} />
                </td>
                <td style={{ ...tdStyle, color: "#A49C95" }}>
                  {new Date(m.created_at).toLocaleDateString()}
                </td>
                <td style={{ ...tdStyle, textAlign: "right", whiteSpace: "nowrap" }}>
                  {!isSelf &&
                    (confirmRemove === m.user_id ? (
                      <span style={{ display: "inline-flex", gap: 2 }}>
                        <button
                          onClick={() => removeMember(m.user_id)}
                          aria-label="Confirm removal"
                          title="Remove member"
                          style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#CC420B" }}
                        >
                          <Check size={14} />
                        </button>
                        <button
                          onClick={() => setConfirmRemove(null)}
                          aria-label="Cancel removal"
                          style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#6E6660" }}
                        >
                          <X size={14} />
                        </button>
                      </span>
                    ) : (
                      <button
                        onClick={() => setConfirmRemove(m.user_id)}
                        aria-label={`Remove ${m.email}`}
                        title="Remove member"
                        style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#A49C95" }}
                      >
                        <Trash2 size={14} />
                      </button>
                    ))}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {invitations.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: "#6E6660", marginBottom: 4 }}>
            Pending invitations
          </h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                {["Email", "Role", "Expires", ""].map((h, i) => (
                  <th key={i} style={thStyle}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {invitations.map((inv) => (
                <tr key={inv.id}>
                  <td style={{ ...tdStyle, color: "#1B1817" }}>{inv.email}</td>
                  <td style={tdStyle}>
                    <RoleBadge role={inv.role} />
                  </td>
                  <td style={{ ...tdStyle, color: "#A49C95" }}>
                    {new Date(inv.expires_at).toLocaleDateString()}
                  </td>
                  <td style={{ ...tdStyle, textAlign: "right" }}>
                    <button
                      onClick={() => revokeInvitation(inv.id)}
                      aria-label={`Revoke invitation for ${inv.email}`}
                      title="Revoke invitation"
                      style={{ border: "none", background: "none", cursor: "pointer", padding: 4, color: "#A49C95" }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: "left",
  fontSize: 11,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: 0.5,
  color: "#A49C95",
  padding: "8px 12px 8px 0",
  borderBottom: "1px solid #E8E2DB",
};

const tdStyle: React.CSSProperties = {
  fontSize: 13,
  color: "#6E6660",
  padding: "10px 12px 10px 0",
  borderBottom: "1px solid #F3EFEA",
  verticalAlign: "middle",
};
