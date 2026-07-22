// Public auth pages: one clean centered card, no product name or logo
// (user decision), no app chrome.
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 400,
          backgroundColor: "#FFFFFF",
          border: "1px solid #E8E2DB",
          borderRadius: 14,
          boxShadow: "0 8px 24px rgba(23,20,18,0.06)",
          padding: 28,
        }}
      >
        {children}
      </div>
    </div>
  );
}
