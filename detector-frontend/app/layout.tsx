import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import Background from "@/components/Background";
import ChatWidget from "@/components/ChatWidget";

const inter = Inter({ subsets: ["latin", "cyrillic"], variable: "--font-inter" });

export const metadata: Metadata = { title: "Detector — kitoblardan aniq qidiruv", description: "So‘z yoki iborani kitoblardan sahifasi bilan toping" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body className={`${inter.variable} antialiased`}>
        <Providers>
          <Background />
          <div className="relative z-10 min-h-screen">{children}</div>
          <ChatWidget />
        </Providers>
      </body>
    </html>
  );
}
