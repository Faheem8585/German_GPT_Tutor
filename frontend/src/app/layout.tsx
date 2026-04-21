import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/layout/Providers";

export const metadata: Metadata = {
  title: {
    default: "GermanGPT Tutor — AI-Powered German Learning",
    template: "%s | GermanGPT Tutor",
  },
  description:
    "Master German from A1 to C2 with AI-powered tutoring, voice practice, gamified lessons, and personalized learning paths. Built for Germany job seekers.",
  keywords: [
    "German learning",
    "Deutsch lernen",
    "AI language tutor",
    "CEFR exam prep",
    "German for jobs",
    "TELC B2 preparation",
    "Goethe certificate",
  ],
  authors: [{ name: "GermanGPT Tutor" }],
  creator: "GermanGPT Tutor",
  openGraph: {
    type: "website",
    title: "GermanGPT Tutor — AI-Powered German Learning",
    description: "Master German from A1 to C2 with AI.",
    siteName: "GermanGPT Tutor",
  },
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "GermanGPT",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0d0d1a" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
