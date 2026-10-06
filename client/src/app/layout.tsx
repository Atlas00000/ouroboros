import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Instrument_Sans } from "next/font/google";

import { AppProviders } from "@/components/providers/app-providers";

import "./globals.css";

const display = Instrument_Sans({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

const ui = IBM_Plex_Sans({
  variable: "--font-ui",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

const numeric = IBM_Plex_Mono({
  variable: "--font-numeric",
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ouroboros",
  description: "Asset intelligence — research context only. Not investment advice.",
  icons: {
    icon: "/logo.svg",
  },
  appleWebApp: {
    capable: true,
    title: "Ouroboros",
    statusBarStyle: "black-translucent",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#090c0b" },
    { media: "(prefers-color-scheme: light)", color: "#f7f4ee" },
  ],
};

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

/**
 * Blocking boot — runs before first paint so stored/system preference
 * wins over SSR defaults (avoids dark→light flash).
 */
const THEME_BOOT = `(function(){try{var k='ouroboros-theme';var t=localStorage.getItem(k);if(t!=='light'&&t!=='dark'&&t!=='system')t='dark';var mode=t==='system'?(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'):t;var r=document.documentElement;r.setAttribute('data-theme',mode);r.classList.remove('light','dark');r.classList.add(mode);}catch(e){}})();`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  const body = (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${display.variable} ${ui.variable} ${numeric.variable} h-full`}
    >
      <head>
        <script
          id="ouroboros-theme-boot"
          dangerouslySetInnerHTML={{ __html: THEME_BOOT }}
        />
      </head>
      <body className="flex min-h-full flex-col bg-ds-canvas text-ds-ink antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );

  if (!clerkEnabled) {
    return body;
  }

  return <ClerkProvider>{body}</ClerkProvider>;
}
