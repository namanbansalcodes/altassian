import "./globals.css";
import type {Metadata} from "next";
import {Providers} from "./providers";

export const metadata: Metadata = {
  title: "Altassian",
  description: "Markdown-first wiki",
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body className="bg-zinc-50 text-zinc-900 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
