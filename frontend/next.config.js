/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: [
      'localhost',
      // Add your CDN domains here
    ],
    formats: ['image/avif', 'image/webp'],
  },
  env: {
    NEXT_PUBLIC_API_GATEWAY_URL: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost',
    NEXT_PUBLIC_SITE_SERVICE_URL: process.env.NEXT_PUBLIC_SITE_SERVICE_URL || 'http://localhost:8010',
    NEXT_PUBLIC_STOREFRONT_SERVICE_URL: process.env.NEXT_PUBLIC_STOREFRONT_SERVICE_URL || 'http://localhost:8011',
    NEXT_PUBLIC_BOOKING_SERVICE_URL: process.env.NEXT_PUBLIC_BOOKING_SERVICE_URL || 'http://localhost:8012',
    NEXT_PUBLIC_LEAD_SERVICE_URL: process.env.NEXT_PUBLIC_LEAD_SERVICE_URL || 'http://localhost:8013',
    NEXT_PUBLIC_CONTENT_SERVICE_URL: process.env.NEXT_PUBLIC_CONTENT_SERVICE_URL || 'http://localhost:8014',
    NEXT_PUBLIC_WIDGET_SERVICE_URL: process.env.NEXT_PUBLIC_WIDGET_SERVICE_URL || 'http://localhost:8015',
    NEXT_PUBLIC_AUTH_SERVICE_URL: process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || 'http://localhost:8000',
  },
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost', '127.0.0.1'],
    },
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/demo-store',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
