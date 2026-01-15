import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  images: { unoptimized: true },

  // Augmenter la limite de taille pour les uploads
  experimental: {
    serverActions: {
      bodySizeLimit: "500mb",
    },
  },

  // Proxy vers le Backend FastAPI (Réseau Docker)
  async rewrites() {
    return [
      {
        source: "/api/python/:path*",
        destination: "http://sms_api:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
