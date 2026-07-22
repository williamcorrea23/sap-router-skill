// Simple white content card. Matches the card style used across the portal.
export default function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={className}
      style={{
        backgroundColor: "#FFFFFF",
        border: "1px solid #E8E2DB",
        borderRadius: 12,
        padding: 24,
      }}
    >
      {children}
    </div>
  );
}
