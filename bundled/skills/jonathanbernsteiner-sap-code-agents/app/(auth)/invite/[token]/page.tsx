"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "../../../../lib/auth/client";
import {
  AuthButton,
  AuthError,
  authInputStyle,
  authLabelStyle,
} from "../../../../components/auth/form";

interface InviteInfo {
  valid: boolean;
  reason?: string;
  email?: string;
  role?: string;
  company?: string;
}

/** Invitation acceptance: set a password, get a profile, land in the app. */
export default function InvitePage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const router = useRouter();
  const [info, setInfo] = useState<InviteInfo | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`/api/invitations/info?token=${encodeURIComponent(token)}`)
      .then((r) => r.json())
      .then(setInfo)
      .catch(() => setInfo({ valid: false, reason: "error" }));
  }, [token]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    setError(null);
    const res = await fetch("/api/invitations/accept", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password, display_name: displayName }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setError(data.error ?? "Could not accept the invitation.");
      setBusy(false);
      return;
    }
    const { error: signInError } = await supabaseBrowser().auth.signInWithPassword({
      email: data.email,
      password,
    });
    if (signInError) {
      // Account exists now — let them sign in manually.
      router.push("/login");
      return;
    }
    router.push("/");
    router.refresh();
  }

  if (!info) {
    return <p style={{ fontSize: 13, color: "#6E6660" }}>Checking your invitation…</p>;
  }

  if (!info.valid) {
    const message =
      info.reason === "accepted"
        ? "This invitation has already been used. Sign in with your email and password instead."
        : "This invitation link is invalid or has expired. Ask your company admin for a new one.";
    return (
      <div>
        <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 8 }}>
          Invitation unavailable
        </h1>
        <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>{message}</p>
        <Link href="/login" style={{ fontSize: 13, color: "#CC420B", fontWeight: 600 }}>
          Go to sign in
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={submit}>
      <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 4 }}>
        Join {info.company}
      </h1>
      <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
        You&apos;ve been invited as <strong>{info.role}</strong>. Set a password to activate your
        account.
      </p>
      <AuthError message={error} />
      <label style={authLabelStyle}>Email</label>
      <input value={info.email} disabled style={{ ...authInputStyle, marginBottom: 14, color: "#6E6660" }} />
      <label style={authLabelStyle} htmlFor="name">
        Your name
      </label>
      <input
        id="name"
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
        placeholder="Shown to your colleagues"
        style={{ ...authInputStyle, marginBottom: 14 }}
      />
      <label style={authLabelStyle} htmlFor="password">
        Password
      </label>
      <input
        id="password"
        type="password"
        required
        autoComplete="new-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ ...authInputStyle, marginBottom: 14 }}
      />
      <label style={authLabelStyle} htmlFor="confirm">
        Repeat password
      </label>
      <input
        id="confirm"
        type="password"
        required
        autoComplete="new-password"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
        style={{ ...authInputStyle, marginBottom: 18 }}
      />
      <AuthButton disabled={busy}>{busy ? "Creating account…" : "Create account"}</AuthButton>
    </form>
  );
}
