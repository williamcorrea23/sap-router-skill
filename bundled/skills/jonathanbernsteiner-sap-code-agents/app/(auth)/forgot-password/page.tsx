"use client";

import { useState } from "react";
import Link from "next/link";
import { supabaseBrowser } from "../../../lib/auth/client";
import { AuthButton, authInputStyle, authLabelStyle } from "../../../components/auth/form";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    // Fire and show the same neutral confirmation regardless of the outcome —
    // this page must never reveal whether an email has an account.
    await supabaseBrowser()
      .auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${window.location.origin}/auth/callback?next=/reset-password`,
      })
      .catch(() => undefined);
    setSent(true);
    setBusy(false);
  }

  if (sent) {
    return (
      <div>
        <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 8 }}>
          Check your inbox
        </h1>
        <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
          If an account exists for <strong>{email.trim()}</strong>, a password-reset link is on its
          way. The link expires after a short time.
        </p>
        <Link href="/login" style={{ fontSize: 13, color: "#CC420B", fontWeight: 600 }}>
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={submit}>
      <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 4 }}>
        Reset your password
      </h1>
      <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
        Enter your account email and we&apos;ll send a reset link.
      </p>
      <label style={authLabelStyle} htmlFor="email">
        Email
      </label>
      <input
        id="email"
        type="email"
        required
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ ...authInputStyle, marginBottom: 18 }}
      />
      <AuthButton disabled={busy}>{busy ? "Sending…" : "Send reset link"}</AuthButton>
      <div style={{ marginTop: 14, textAlign: "center" }}>
        <Link href="/login" style={{ fontSize: 13, color: "#6E6660" }}>
          Back to sign in
        </Link>
      </div>
    </form>
  );
}
