"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "../../../lib/auth/client";
import { AuthButton, AuthError, authInputStyle, authLabelStyle } from "../../../components/auth/form";

/**
 * Lands here from the reset email (via /auth/callback, which established a
 * recovery session). Without such a session the link was bad or expired.
 */
export default function ResetPasswordPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);
  const [hasSession, setHasSession] = useState(false);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    supabaseBrowser()
      .auth.getUser()
      .then(({ data }) => {
        setHasSession(!!data.user);
        setChecking(false);
      });
  }, []);

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
    const { error: updateError } = await supabaseBrowser().auth.updateUser({ password });
    if (updateError) {
      setError(updateError.message);
      setBusy(false);
      return;
    }
    router.push("/");
    router.refresh();
  }

  if (checking) {
    return <p style={{ fontSize: 13, color: "#6E6660" }}>Checking your reset link…</p>;
  }

  if (!hasSession) {
    return (
      <div>
        <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 8 }}>
          Link invalid or expired
        </h1>
        <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
          This password-reset link is no longer valid. Request a new one and try again.
        </p>
        <Link href="/forgot-password" style={{ fontSize: 13, color: "#CC420B", fontWeight: 600 }}>
          Request a new link
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={submit}>
      <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 18 }}>
        Choose a new password
      </h1>
      <AuthError message={error} />
      <label style={authLabelStyle} htmlFor="password">
        New password
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
        Repeat new password
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
      <AuthButton disabled={busy}>{busy ? "Saving…" : "Set new password"}</AuthButton>
    </form>
  );
}
