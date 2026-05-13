/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  // Proxy /api/* to the backend so we don't deal with CORS in dev.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.WHENDO_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
