import Card from "./Card";

// Drop-in placeholder body for a page you haven't built yet.
// Shows a title, subtitle, and a few skeleton blocks so the layout reads as
// "real" while you flesh out the actual content later.
export default function PagePlaceholder({
  title,
  subtitle = "Placeholder content — replace this when you build the page.",
  blocks = 3,
}: {
  title: string;
  subtitle?: string;
  blocks?: number;
}) {
  return (
    <div style={{ padding: 32 }}>
      <div style={{ maxWidth: 960 }}>
        {/* Title */}
        <h2 style={{ fontSize: 22, fontWeight: 700, color: "#1B1817", margin: 0 }}>
          {title}
        </h2>
        <p style={{ fontSize: 14, color: "#6E6660", marginTop: 6, marginBottom: 24 }}>
          {subtitle}
        </p>

        {/* Skeleton content blocks */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {Array.from({ length: blocks }).map((_, i) => (
            <Card key={i}>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <Bar width="40%" />
                <Bar width="90%" />
                <Bar width="75%" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

function Bar({ width }: { width: string }) {
  return (
    <div
      style={{
        width,
        height: 12,
        borderRadius: 6,
        backgroundColor: "#F3EDE6",
      }}
    />
  );
}
