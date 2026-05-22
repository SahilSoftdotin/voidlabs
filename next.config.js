/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  basePath: '/voidlabs',
  assetPrefix: '/voidlabs',
  images: {
    unoptimized: true,
    formats: ['image/webp', 'image/avif'],
  },
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,
  trailingSlash: false,
  experimental: {
    optimizePackageImports: ['react', 'react-dom'],
  },
};

export default nextConfig;
