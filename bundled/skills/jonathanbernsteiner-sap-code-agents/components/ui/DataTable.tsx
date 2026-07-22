"use client";

import { Fragment, useState, type CSSProperties, type ReactNode } from "react";

export interface Column<T> {
  header: string;
  render: (row: T, index: number) => ReactNode;
  width?: string | number;
  nowrap?: boolean;
  align?: "left" | "right";
}

const thStyle: CSSProperties = {
  textAlign: "left",
  whiteSpace: "nowrap",
  fontSize: 11,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: 0.5,
  color: "#A49C95",
  padding: "8px 12px 8px 0",
  borderBottom: "1px solid #E8E2DB",
};

const tdStyle: CSSProperties = {
  fontSize: 13,
  color: "#6E6660",
  padding: "10px 12px 10px 0",
  borderBottom: "1px solid #F3EFEA",
  verticalAlign: "top",
};

/**
 * Shared data table — same idiom as the settings tables (uppercase hairline
 * header, warm dividers). Optional `expandContent` adds a chevron column and
 * makes rows with content clickable; the expanded panel spans the full width.
 */
export default function DataTable<T>({
  columns,
  rows,
  rowKey,
  expandContent,
  emptyText = "None.",
}: {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T, index: number) => string;
  /** return null for rows that have nothing to expand */
  expandContent?: (row: T, index: number) => ReactNode | null;
  emptyText?: string;
}) {
  const [open, setOpen] = useState<Set<string>>(new Set());
  if (rows.length === 0) return <p style={{ fontSize: 13, color: "#6E6660", margin: 0 }}>{emptyText}</p>;

  const toggle = (k: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(k)) next.delete(k);
      else next.add(k);
      return next;
    });

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          {expandContent && <th style={{ ...thStyle, width: 22 }} aria-label="Expand" />}
          {columns.map((c, i) => (
            <th key={i} style={{ ...thStyle, width: c.width, textAlign: c.align ?? "left" }}>
              {c.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => {
          const k = rowKey(row, i);
          const detail = expandContent?.(row, i) ?? null;
          const expanded = open.has(k);
          return (
            <Fragment key={k}>
              <tr
                onClick={detail ? () => toggle(k) : undefined}
                style={{ cursor: detail ? "pointer" : "default" }}
              >
                {expandContent && (
                  <td style={{ ...tdStyle, color: "#A49C95", fontSize: 11, paddingRight: 0 }}>
                    {detail ? (expanded ? "▾" : "▸") : ""}
                  </td>
                )}
                {columns.map((c, j) => (
                  <td
                    key={j}
                    style={{
                      ...tdStyle,
                      whiteSpace: c.nowrap ? "nowrap" : undefined,
                      textAlign: c.align ?? "left",
                    }}
                  >
                    {c.render(row, i)}
                  </td>
                ))}
              </tr>
              {expanded && detail && (
                <tr>
                  <td
                    colSpan={columns.length + 1}
                    style={{ ...tdStyle, paddingTop: 0, paddingBottom: 12, backgroundColor: "#FFFFFF" }}
                  >
                    {detail}
                  </td>
                </tr>
              )}
            </Fragment>
          );
        })}
      </tbody>
    </table>
  );
}
