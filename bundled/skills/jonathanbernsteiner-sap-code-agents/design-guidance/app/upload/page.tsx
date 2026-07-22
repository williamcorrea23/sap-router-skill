"use client";

import { Upload } from "lucide-react";

// Upload page — placeholder drop zone. No real upload logic yet.
export default function UploadPage() {
  return (
    <div style={{ padding: 32 }}>
      <div style={{ maxWidth: 720 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#1B1817", margin: 0 }}>
          Upload
        </h2>
        <p style={{ fontSize: 14, color: "#6E6660", marginTop: 6, marginBottom: 24 }}>
          Placeholder upload area — wire up file handling when you build it.
        </p>

        <label
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 12,
            padding: "48px 24px",
            border: "2px dashed #DBD2C9",
            borderRadius: 12,
            backgroundColor: "#FCEDE4",
            color: "#6E6660",
            cursor: "pointer",
            textAlign: "center",
          }}
        >
          <Upload size={28} style={{ color: "#F04E0D" }} />
          <div style={{ fontSize: 14, fontWeight: 500, color: "#1B1817" }}>
            Drag &amp; drop a file here, or click to browse
          </div>
          <div style={{ fontSize: 12, color: "#A49C95" }}>
            (This is a placeholder — no file is uploaded yet.)
          </div>
          <input type="file" style={{ display: "none" }} />
        </label>
      </div>
    </div>
  );
}
