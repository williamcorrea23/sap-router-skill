import type { Metadata } from "next";
import "./globals.css";
import { PRODUCT_DESCRIPTION, PRODUCT_NAME } from "../lib/config";

export const metadata: Metadata = {
  title: PRODUCT_NAME,
  description: PRODUCT_DESCRIPTION,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: "#F6F4F1" }}>{children}</body>
    </html>
  );
}
