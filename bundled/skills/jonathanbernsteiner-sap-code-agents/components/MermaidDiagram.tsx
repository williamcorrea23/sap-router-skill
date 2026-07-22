"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Renders Mermaid text computed by the server (lib/diagram). The diagram
 * definition is never written by the LLM — this component only displays what
 * the application computed from call_edges.
 */
export default function MermaidDiagram({ definition }: { definition: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function render() {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "neutral",
          themeVariables: {
            fontFamily: "DM Sans, system-ui, sans-serif",
            primaryColor: "#FAF8F5",
            primaryBorderColor: "#E8E2DB",
            primaryTextColor: "#1B1817",
            lineColor: "#A49C95",
          },
        });
        const { svg } = await mermaid.render(`d${Math.random().toString(36).slice(2)}`, definition);
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      }
    }
    render();
    return () => {
      cancelled = true;
    };
  }, [definition]);

  if (error) {
    return (
      <pre style={{ fontSize: 12, color: "#6E6660", fontFamily: "JetBrains Mono, monospace", whiteSpace: "pre-wrap" }}>
        {definition}
      </pre>
    );
  }
  return <div ref={ref} style={{ overflowX: "auto" }} />;
}
