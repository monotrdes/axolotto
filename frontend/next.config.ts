import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["axolot.to", "play.axolot.to"],
  async redirects() {
    return [
      { source: '/join', destination: '/', permanent: true },
      { source: '/admin', destination: '/play/admin', permanent: false },
    ]
  },
};

export default nextConfig;
