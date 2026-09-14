import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import { AppProviders } from "@/components/providers/app-providers";

import "./globals.css";

const ui = Inter({
  variable: "--font-ui",
  subsets: ["latin"],
  display: "swap",
});

const numeric = JetBrains_Mono({
  variable: "--font-numeric",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ouroboros",
  description: "Asset intelligence — research context only. Not investment advice.",
  icons: {
    icon: "/logo.svg",
  },
};

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

export default function RootLayout({ children }: LayoutProps<"/">) {
  const body = (
    <html lang="en" className={`${ui.variable} ${numeric.variable} dark h-full`}>
      <body className="min-h-full flex flex-col bg-background text-foreground antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );

  if (!clerkEnabled) {
    return body;
  }

  return <ClerkProvider>{body}</ClerkProvider>;
}
