"use client";

/**
 * Connections → Connect a system. Source-type tiles (git repository today,
 * SAP-system RFC extractor planned) plus the ingest form. A successful
 * submit jumps to Connected systems, where the pipeline status is visible.
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { GitBranch, Server } from "lucide-react";
import Card from "../../../components/ui/Card";

/** Mirrors lib/ingest/git.ts workspaceNameForUrl — preview only. */
function derivedName(url: string): string {
  const base = url.trim().replace(/\/+$/, "").replace(/\.git$/, "").split("/").pop() ?? "";
  return base.toLowerCase().replace(/[^a-z0-9-_]/g, "-").replace(/^-+|-+$/g, "");
}

/** Mirrors lib/ingest/git.ts normalizeWorkspaceName — preview only. */
function normalizedName(raw: string): string {
  return raw.trim().toLowerCase().replace(/[^a-z0-9-_]+/g, "-").replace(/^-+|-+$/g, "");
}

/** Source-type tile — git is the one selectable type today; the RFC
 *  extractor tile marks where a live SAP-system connection plugs in. */
function SourceTypeTile({
  icon, title, description, selected, disabled, badge, onClick,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  selected?: boolean;
  disabled?: boolean;
  badge?: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-pressed={selected}
      style={{
        flex: "1 1 260px", textAlign: "left", fontFamily: "inherit", cursor: disabled ? "default" : "pointer",
        backgroundColor: selected ? "#FCEDE4" : "#FFFFFF",
        border: `1px solid ${selected ? "#F04E0D" : "#E8E2DB"}`,
        borderRadius: 10, padding: "12px 14px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
        <span style={{ color: disabled ? "#A49C95" : selected ? "#CC420B" : "#6E6660", display: "inline-flex" }}>{icon}</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: disabled ? "#6E6660" : "#1B1817" }}>{title}</span>
        {badge && (
          <span style={{ fontSize: 11, fontWeight: 600, color: "#6E6660", backgroundColor: "#F0EDE8", borderRadius: 6, padding: "1px 7px" }}>
            {badge}
          </span>
        )}
      </div>
      <div style={{ fontSize: 12, color: "#A49C95", lineHeight: 1.45 }}>{description}</div>
    </button>
  );
}

export default function ConnectSystemPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const effectiveName = name.trim() ? normalizedName(name) : derivedName(url);

  const connect = async () => {
    if (!url.trim() || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), ...(name.trim() ? { name: name.trim() } : {}) }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error ?? "Ingestion could not be started.");
      } else {
        router.push("/connections/systems");
        return;
      }
    } catch {
      setError("Ingestion could not be started.");
    }
    setSubmitting(false);
  };

  return (
    <Card>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>Connect a system</h2>

      {/* Source types — git today; the RFC extractor is the planned second type */}
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
        <SourceTypeTile
          icon={<GitBranch size={16} />}
          title="Git repository"
          description="Public HTTPS git URL of an ABAP repository (abapGit layout)."
          selected
        />
        <SourceTypeTile
          icon={<Server size={16} />}
          title="SAP system — RFC extractor"
          description="Direct extraction from a live SAP system plugs in here; downstream ingestion is identical."
          disabled
          badge="Planned"
        />
      </div>

      <p style={{ fontSize: 12, color: "#6E6660", marginBottom: 12 }}>
        Caps: 3,000 ABAP files / 25 MB source. One ingestion runs at a time; further requests queue.
      </p>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && connect()}
          placeholder="https://github.com/abap2xlsx/abap2xlsx"
          style={{
            flex: "2 1 320px", fontSize: 13, fontFamily: "JetBrains Mono, monospace", padding: "9px 12px",
            backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 8, outline: "none",
          }}
        />
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && connect()}
          placeholder={derivedName(url) || "system name (optional)"}
          style={{
            flex: "1 1 180px", fontSize: 13, fontFamily: "JetBrains Mono, monospace", padding: "9px 12px",
            backgroundColor: "#FAF8F5", border: "1px solid #E8E2DB", borderRadius: 8, outline: "none",
          }}
        />
        <button
          onClick={connect}
          disabled={submitting || !url.trim()}
          style={{
            fontSize: 13, fontWeight: 600, color: "#FFFFFF",
            backgroundColor: submitting || !url.trim() ? "#A49C95" : "#F04E0D",
            border: "none", borderRadius: 8, padding: "9px 16px",
            cursor: submitting || !url.trim() ? "default" : "pointer", fontFamily: "inherit",
          }}
        >
          {submitting ? "Starting…" : "Ingest"}
        </button>
      </div>
      {/* Usage statistics are runtime data (ST03N / SCMON / UPL) and cannot
          come from a repository — the report states that plainly rather than
          estimating. Synthetic usage exists for operator-run demo systems
          only (npm run gen-usage), never as a client-facing option. */}
      <p style={{ fontSize: 12, color: "#6E6660", marginTop: 12, marginBottom: 0 }}>
        Retirement analysis needs execution statistics (ST03N / SCMON / UPL) from the SAP system
        itself; a repository carries none. Without them the report analyzes incompatibilities and
        states that usage data is unavailable, rather than estimating it.
      </p>
      {effectiveName && (
        <p style={{ fontSize: 11, color: "#A49C95", marginTop: 8, marginBottom: 0 }}>
          Will be created as{" "}
          <span style={{ fontFamily: "JetBrains Mono, monospace", color: "#6E6660" }}>{effectiveName}</span>
          {" "}— lowercase letters, numbers, - and _.
        </p>
      )}
      {error && <p style={{ fontSize: 12, color: "#CC420B", marginTop: 8, marginBottom: 0 }}>{error}</p>}
    </Card>
  );
}
