import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import dynamic from "next/dynamic";
import "./globals.css";
import { ReactQueryProvider } from "@/lib/query";

// Lazy-load MobileNav — it's a client component with event handlers and state;
// deferring it reduces the initial JS bundle for the server-rendered shell.
const MobileNav = dynamic(() => import("@/components/MobileNav").then(m => ({ default: m.MobileNav })), {
  ssr: false,
});

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Altassian",
  description: "Altassian frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ReactQueryProvider>
          <MobileNav />
          <main className="pb-16 md:pb-6">
            {children}
          </main>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
