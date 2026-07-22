"use client";

import { useEffect, useState } from "react";
import Card from "../../../components/ui/Card";
import {
  helperStyle,
  inputStyle,
  labelStyle,
  primaryButtonStyle,
  readOnlyInputStyle,
} from "../../../components/ui/formStyles";
import { profileChanged, useProfile } from "../../../components/useProfile";
import { supabaseBrowser } from "../../../lib/auth/client";

/** Profile settings (Change Order 03): server-backed, per-account. */
export default function SettingsPage() {
  const profile = useProfile();
  const [name, setName] = useState("");
  const [saved, setSaved] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwMessage, setPwMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [pwBusy, setPwBusy] = useState(false);

  useEffect(() => {
    if (profile.loaded) setName(profile.name);
  }, [profile.loaded, profile.name]);

  const nameDirty = profile.loaded && name.trim() !== profile.name;
  const pwFilled = currentPassword !== "" && newPassword !== "" && confirmPassword !== "";

  async function saveName() {
    const res = await fetch("/api/profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: name }),
    });
    if (res.ok) {
      profileChanged();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  }

  async function changePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwMessage(null);
    if (newPassword.length < 8) {
      setPwMessage({ ok: false, text: "New password must be at least 8 characters." });
      return;
    }
    if (newPassword !== confirmPassword) {
      setPwMessage({ ok: false, text: "New passwords do not match." });
      return;
    }
    setPwBusy(true);
    const supabase = supabaseBrowser();
    // Verify the current password first (updateUser alone doesn't ask for it).
    const { error: reauthError } = await supabase.auth.signInWithPassword({
      email: profile.email,
      password: currentPassword,
    });
    if (reauthError) {
      setPwMessage({ ok: false, text: "Current password is incorrect." });
      setPwBusy(false);
      return;
    }
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) {
      setPwMessage({ ok: false, text: error.message });
    } else {
      setPwMessage({ ok: true, text: "Password changed." });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    }
    setPwBusy(false);
  }

  return (
    <>
      <Card>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Profile</h2>
        <p style={{ fontSize: 13, color: "#6E6660", marginBottom: 18 }}>
          Your name is shown to colleagues (e.g. on shared company chats).
        </p>
        {/* fields side by side — the card spans the full pane */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 14, marginBottom: 18 }}>
          <div>
            <label style={labelStyle}>Display name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Joni Bernsteiner"
              style={inputStyle}
            />
          </div>
          <div>
            <label style={labelStyle}>Email</label>
            <input value={profile.email} disabled style={readOnlyInputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Company</label>
            <input value={profile.company} disabled style={readOnlyInputStyle} />
            <p style={helperStyle}>Managed by your company admin.</p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button onClick={saveName} disabled={!nameDirty} style={primaryButtonStyle(!nameDirty)}>
            Save
          </button>
          {saved && <span style={{ fontSize: 13, color: "#CC420B" }}>Saved.</span>}
        </div>
      </Card>

      <Card>
        <form onSubmit={changePassword}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 18 }}>Change password</h2>
          {pwMessage && (
            <div
              role="alert"
              style={{
                fontSize: 13,
                color: pwMessage.ok ? "#1B1817" : "#CC420B",
                backgroundColor: pwMessage.ok ? "#F3EFEA" : "#FCEDE4",
                borderRadius: 8,
                padding: "8px 12px",
                marginBottom: 14,
              }}
            >
              {pwMessage.text}
            </div>
          )}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 14, marginBottom: 18 }}>
            <div>
              <label style={labelStyle}>Current password</label>
              <input
                type="password"
                required
                autoComplete="current-password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>New password</label>
              <input
                type="password"
                required
                autoComplete="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Repeat new password</label>
              <input
                type="password"
                required
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                style={inputStyle}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={pwBusy || !pwFilled}
            style={primaryButtonStyle(pwBusy || !pwFilled)}
          >
            {pwBusy ? "Changing…" : "Change password"}
          </button>
        </form>
      </Card>
    </>
  );
}
