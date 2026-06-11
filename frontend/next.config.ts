import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["axolot.to", "play.axolot.to", "192.168.100.11"],
  async redirects() {
    return [
      { source: '/join', destination: '/', permanent: true },
      { source: '/admin', destination: '/play/admin', permanent: false },
    ]
  },
  // Proxy same-origin al backend en dev: el navegador solo habla con :3001
  // y Next reenvía a :8001 — evita CORS y permite probar desde LAN/móvil.
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8001/api/v1/:path*',
      },
    ]
  },
};

export default nextConfig;
