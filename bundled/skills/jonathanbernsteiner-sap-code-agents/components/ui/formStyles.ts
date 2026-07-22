import type { CSSProperties } from "react";

// Shared form styles for the settings screens so Profile, Change Password and
// Company stay visually consistent (design-guidance palette).

/** Inputs stay readable on desktop even when the card is wider. */
export const FIELD_MAX_WIDTH = 480;

/** Base input look without sizing — for inputs laid out by flex (e.g. inline forms). */
export const inputBaseStyle: CSSProperties = {
  fontSize: 14,
  padding: "9px 12px",
  borderRadius: 8,
  border: "1px solid #E8E2DB",
  backgroundColor: "#FAF8F5",
  color: "#1B1817",
  outline: "none",
  fontFamily: "inherit",
};

/** Standard stacked form input. */
export const inputStyle: CSSProperties = {
  ...inputBaseStyle,
  display: "block",
  width: "100%",
  maxWidth: FIELD_MAX_WIDTH,
};

/** Read-only field: muted, not focusable, must not look editable. */
export const readOnlyInputStyle: CSSProperties = {
  ...inputStyle,
  backgroundColor: "#F3EFEA",
  color: "#6E6660",
  cursor: "default",
};

export const labelStyle: CSSProperties = {
  display: "block",
  fontSize: 13,
  color: "#6E6660",
  marginBottom: 6,
};

/** Small explanatory text under a field. */
export const helperStyle: CSSProperties = {
  fontSize: 12,
  color: "#A49C95",
  marginTop: 6,
};

/** Primary (save) button, bottom-left of each card. */
export function primaryButtonStyle(disabled: boolean): CSSProperties {
  return {
    fontSize: 14,
    fontWeight: 600,
    padding: "9px 20px",
    borderRadius: 8,
    border: "none",
    cursor: disabled ? "default" : "pointer",
    backgroundColor: "#F04E0D",
    color: "#FFFFFF",
    fontFamily: "inherit",
    opacity: disabled ? 0.5 : 1,
  };
}
