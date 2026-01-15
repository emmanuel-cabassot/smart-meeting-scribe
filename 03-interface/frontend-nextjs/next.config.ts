import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ⚡ CRITIQUE : Permet de générer un dossier minimal pour Docker
  output: "standalone",

  // Sécurité
  poweredByHeader: false,

  // Optimisation images (nécessaire pour Docker sans libs externes)
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
