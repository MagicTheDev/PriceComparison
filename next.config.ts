import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",  // allow all hostnames
      },
    ],
  },
};

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

/** @type {import('next').NextConfig} */
module.exports = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${FASTAPI_URL}/:path*` }];
  },
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }], // ok for prototyping
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
