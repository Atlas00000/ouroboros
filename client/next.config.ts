import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Allow both localhost and 127.0.0.1 in dev (HMR / client chunks).
  // Without this, opening http://127.0.0.1:3001 blocks hydration and charts stay on "Loading".
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
