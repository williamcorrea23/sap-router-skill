"use client";

/** Shared styling + primitives for the auth pages (centered-card layout). */

export const authInputStyle: React.CSSProperties = {
  width: "100%",
  fontSize: 14,
  padding: "9px 12px",
  borderRadius: 8,
  border: "1px solid #E8E2DB",
  backgroundColor: "#FAF8F5",
  color: "#1B1817",
  outline: "none",
  fontFamily: "inherit",
};

export const authLabelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 13,
  color: "#6E6660",
  marginBottom: 6,
};

export function AuthButton({
  children,
  disabled,
}: {
  children: React.ReactNode;
  disabled?: boolean;
}) {
  return (
    <button
      type="submit"
      disabled={disabled}
      style={{
        width: "100%",
        fontSize: 14,
        fontWeight: 600,
        padding: "10px 20px",
        borderRadius: 8,
        border: "none",
        cursor: disabled ? "default" : "pointer",
        backgroundColor: disabled ? "#E8E2DB" : "#F04E0D",
        color: disabled ? "#A49C95" : "#FFFFFF",
        fontFamily: "inherit",
      }}
    >
      {children}
    </button>
  );
}

export function AuthError({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      style={{
        fontSize: 13,
        color: "#CC420B",
        backgroundColor: "#FCEDE4",
        borderRadius: 8,
        padding: "8px 12px",
        marginBottom: 14,
      }}
    >
      {message}
    </div>
  );
}
