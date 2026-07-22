"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { supabaseBrowser } from "../../../lib/auth/client";
import { AuthButton, AuthError, authInputStyle, authLabelStyle } from "../../../components/auth/form";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(
    params.get("error") === "auth-link" ? "That link is invalid or has expired." : null
  );
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const { error: signInError } = await supabaseBrowser().auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    if (signInError) {
      // Generic on purpose — never reveal whether the email exists.
      setError("Invalid email or password.");
      setBusy(false);
      return;
    }
    const next = params.get("next");
    router.push(next && next.startsWith("/") ? next : "/");
    router.refresh();
  }

  return (
    <form onSubmit={submit}>
      <h1 style={{ fontSize: 17, fontWeight: 600, color: "#1B1817", marginBottom: 4 }}>Sign in</h1>
      <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
        Access is by invitation — ask your company admin if you don&apos;t have an account.
      </p>
      <AuthError message={error} />
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
        style={{ ...authInputStyle, marginBottom: 14 }}
      />
      <label style={authLabelStyle} htmlFor="password">
        Password
      </label>
      <input
        id="password"
        type="password"
        required
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ ...authInputStyle, marginBottom: 18 }}
      />
      <AuthButton disabled={busy}>{busy ? "Signing in…" : "Sign in"}</AuthButton>
      <div style={{ marginTop: 14, textAlign: "center" }}>
        <Link href="/forgot-password" style={{ fontSize: 13, color: "#6E6660" }}>
          Forgot your password?
        </Link>
      </div>
    </form>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
