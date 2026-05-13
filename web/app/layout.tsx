import type { Metadata } from "next";
import { JetBrains_Mono, Geist } from "next/font/google";

import { LocaleProvider } from "@/lib/locale-context";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "whendo — Tell your computer when to do things",
  description:
    "Self-hosted personal automation. Plain English or YAML. Open source.",
  icons: {
    icon: [
      { url: "/logo.svg", type: "image/svg+xml" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${jetbrainsMono.variable} ${geistSans.variable}`}>
      <body className="min-h-screen">
        <LocaleProvider>
          <div className="relative z-10">{children}</div>
        </LocaleProvider>
      </body>
    </html>
  );
}
